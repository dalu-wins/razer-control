from gi.repository import Gtk, Adw, Gdk

class ColorGroup(Adw.PreferencesGroup):
    PRESET_COLORS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF", "#FFFFFF"]

    def __init__(self, serial, razer_manager, get_effect_callback):
        super().__init__(title="Color")
        self.serial = serial
        self.manager = razer_manager
        self.get_effect_callback = get_effect_callback

        self._build_ui()
        self._connect_signals()
        self._load_initial_state()

    def _build_ui(self):
        # Presets
        self.preset_row = Adw.ActionRow(title="Quick Presets")
        self.color_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.color_controls.set_valign(Gtk.Align.CENTER)
        
        for hex_color in self.PRESET_COLORS:
            rgba = Gdk.RGBA()
            rgba.parse(hex_color)
            btn = Gtk.Button(css_classes=["circular", "color-preset-btn"])
            dot = Gtk.Box(width_request=18, height_request=18, css_classes=["color-dot"])
            self._apply_widget_color(dot, hex_color)
            btn.set_child(dot)
            btn.connect("clicked", lambda _, r=rgba: self.color_button.set_rgba(r))
            self.color_controls.append(btn)
            
        self.preset_row.add_suffix(self.color_controls)
        self.add(self.preset_row)

        # Custom Color
        self.custom_color_row = Adw.ActionRow(title="Custom Color")
        self.color_button = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog())
        self.color_button.set_valign(Gtk.Align.CENTER)
        self.custom_color_row.add_suffix(self.color_button)
        self.add(self.custom_color_row)

    def _apply_widget_color(self, widget, hex_color):
        provider = Gtk.CssProvider()
        provider.load_from_data(f"box {{ background-color: {hex_color}; border-radius: 10px; }}".encode())
        widget.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _load_initial_state(self):
        state = self.manager.get_current_state(self.serial)
        if state:
            rgba = Gdk.RGBA()
            rgba.red, rgba.green, rgba.blue = state['r']/255, state['g']/255, state['b']/255
            
            self.color_button.handler_block_by_func(self._on_color_changed)
            self.color_button.set_rgba(rgba)
            self.color_button.handler_unblock_by_func(self._on_color_changed)

    def _connect_signals(self):
        self.color_button.connect("notify::rgba", self._on_color_changed)

    def _on_color_changed(self, *args):
        rgba = self.color_button.get_rgba()
        r, g, b = [int(c * 255) for c in [rgba.red, rgba.green, rgba.blue]]
        effect = self.get_effect_callback()
        self.manager.set_effect(effect, r, g, b, device_serial=self.serial)