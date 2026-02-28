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
        """Initialize the main layout and widgets."""
        self.root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.root_box.set_margin_top(20)
        self.root_box.set_margin_bottom(20)
        self.root_box.set_margin_start(20)
        self.root_box.set_margin_end(20)
        self.set_child(self.root_box)

        # Effect selection section
        self.root_box.append(Gtk.Label(label="Effect", xalign=0, css_classes=["heading"]))
        self.dropdown = Gtk.DropDown.new_from_strings(self.supported_effects)
        self.root_box.append(self.dropdown)

        # Color management section
        self.color_group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.color_group.append(Gtk.Label(label="Color", xalign=0, css_classes=["heading"]))
        
        self.color_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self._setup_preset_buttons()
        self._setup_color_picker()
        
        self.color_group.append(self.color_controls)
        self.root_box.append(self.color_group)

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

    def _setup_color_picker(self):
        """Setup the main color dialog button to fill remaining width."""
        self.color_button = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog())
        self.color_button.set_hexpand(True)
        self.color_button.set_halign(Gtk.Align.FILL)
        self.color_controls.append(self.color_button)

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

    def _update_visibility(self):
        """Show/hide color controls based on selected effect."""
        idx = self.dropdown.get_selected()
        effect = self.supported_effects[idx] if idx != -1 else ""
        needs_color = effect in ['static', 'breathSingle', 'reactive']
        self.color_group.set_visible(needs_color)

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