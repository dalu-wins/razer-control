from gi.repository import Gtk, Gdk, Adw

class DevicePage(Adw.Bin):
    """UI page for managing a single Razer device's effects and colors."""
    
    PRESET_COLORS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF", "#FFFFFF"]

    def __init__(self, device_data, razer_manager):
        super().__init__()
        self.manager = razer_manager
        self.serial = device_data['fx']._serial
        self.supported_effects = self.manager.get_all_supported_effects(self.serial)

        self._build_ui()
        self._load_initial_state()
        self._connect_signals()
    def _build_ui(self):
        """Build a structured settings page with separate rows for presets and picker."""
        self.clamp = Adw.Clamp(maximum_size=600)
        self.set_child(self.clamp)

        # Main layout container
        self.root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        self.clamp.set_child(self.root_box)

        # --- General Settings Group ---
        self.general_group = Adw.PreferencesGroup(title="Device Settings")
        self.root_box.append(self.general_group)

        # Effect selection row
        self.effect_row = Adw.ActionRow(title="Lighting Effect")
        self.dropdown = Gtk.DropDown.new_from_strings(self.supported_effects)
        self.dropdown.set_valign(Gtk.Align.CENTER)
        self.effect_row.add_suffix(self.dropdown)
        self.general_group.add(self.effect_row)

        # --- Color Management Group ---
        self.color_group = Adw.PreferencesGroup(title="Color")
        self.root_box.append(self.color_group)

        # Row 1: Quick Presets
        self.preset_row = Adw.ActionRow(title="Quick Presets")
        self.color_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.color_controls.set_valign(Gtk.Align.CENTER)
        self._setup_preset_buttons()
        self.preset_row.add_suffix(self.color_controls)
        self.color_group.add(self.preset_row)

        # Row 2: Manual Custom Color
        self.custom_color_row = Adw.ActionRow(title="Custom Color")
        self._setup_color_picker() # Now adds self.color_button
        self.color_button.set_valign(Gtk.Align.CENTER)
        self.custom_color_row.add_suffix(self.color_button)
        self.color_group.add(self.custom_color_row)

    def _setup_color_picker(self):
        """Initialize the color dialog button."""
        # Removed hexpand as it's now contained within an ActionRow suffix
        self.color_button = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog())

    def _update_visibility(self):
        """Toggle the entire color group visibility."""
        idx = self.dropdown.get_selected()
        effect = self.supported_effects[idx] if idx != -1 else ""
        needs_color = effect in ['static', 'breathSingle', 'reactive']
        
        # Shows/Hides the entire section including Presets and Custom Color
        self.color_group.set_visible(needs_color)   

    def _setup_preset_buttons(self):
        """Create quick-select color buttons."""
        for hex_color in self.PRESET_COLORS:
            rgba = Gdk.RGBA()
            rgba.parse(hex_color)

            btn = Gtk.Button(css_classes=["circular", "color-preset-btn"])
            dot = Gtk.Box(width_request=18, height_request=18, css_classes=["color-dot"])
            self._apply_widget_color(dot, hex_color)
            
            btn.set_child(dot)
            btn.connect("clicked", self._on_preset_clicked, rgba)
            self.color_controls.append(btn)

    def _apply_widget_color(self, widget, hex_color):
        """Apply background color to a widget using CSS."""
        provider = Gtk.CssProvider()
        css = f"box {{ background-color: {hex_color}; border-radius: 10px; }}"
        provider.load_from_data(css.encode())
        widget.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _load_initial_state(self):
        """Sync UI with current hardware state."""
        state = self.manager.get_current_state(self.serial)
        if not state:
            return

        if state['effect'] in self.supported_effects:
            self.dropdown.set_selected(self.supported_effects.index(state['effect']))

        rgba = Gdk.RGBA()
        rgba.red, rgba.green, rgba.blue, rgba.alpha = (
            state['r'] / 255, state['g'] / 255, state['b'] / 255, 1.0
        )
        self.color_button.set_rgba(rgba)
        self._update_visibility()

    def _connect_signals(self):
        """Attach hardware update callbacks."""
        self.dropdown.connect("notify::selected", self._on_ui_changed)
        self.color_button.connect("notify::rgba", self._on_ui_changed)

    def _on_preset_clicked(self, _btn, rgba):
        """Handle preset selection by updating the main picker."""
        self.color_button.set_rgba(rgba)

    def _on_ui_changed(self, *args):
        """Update hardware when UI changes."""
        self._update_visibility()
        idx = self.dropdown.get_selected()
        if idx == -1: 
            return

        rgba = self.color_button.get_rgba()
        r, g, b = [int(c * 255) for c in [rgba.red, rgba.green, rgba.blue]]
        self.manager.set_effect(self.supported_effects[idx], r, g, b, device_serial=self.serial)