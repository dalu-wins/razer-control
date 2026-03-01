from gi.repository import Adw, Gtk, Gdk

from razer_control.ui.components.color_picker import ColorPickerWindow

class ColorGroup(Adw.PreferencesGroup):
    PRESET_COLORS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF", "#FFFFFF"]

    def __init__(self, serial, razer_manager, get_effect_callback):
        super().__init__(title="Color")
        self.serial = serial
        self.manager = razer_manager
        self.get_effect_callback = get_effect_callback
        self.picker_window = None 

        self._build_ui()
        self._load_initial_state()

    def _build_ui(self):
        # 1. Presets
        self.preset_row = Adw.ActionRow(title="Quick Presets")
        self.color_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.color_controls.set_valign(Gtk.Align.CENTER)
        
        for hex_color in self.PRESET_COLORS:
            rgba = Gdk.RGBA()
            rgba.parse(hex_color)
            btn = Gtk.Button(css_classes=["circular", "color-preset-btn"])
            dot = Gtk.Box(width_request=20, height_request=20)
            self._apply_preset_style(btn, dot, hex_color)
            btn.set_child(dot)
            btn.connect("clicked", self._on_preset_clicked, rgba)
            self.color_controls.append(btn)
                    
        self.preset_row.add_suffix(self.color_controls)
        self.add(self.preset_row)

        # Custom Color Row
        self.custom_color_row = Adw.ActionRow(title="Custom Color")
        
        # Der Button, der das Fenster öffnet
        self.open_picker_btn = Gtk.Button(valign=Gtk.Align.CENTER, css_classes=["circular"])
        
        # Die farbige Vorschau im Button
        self.color_preview_dot = Gtk.Box(width_request=24, height_request=24)
        self.open_picker_btn.set_child(self.color_preview_dot)
        
        self.open_picker_btn.connect("clicked", self._on_open_picker)
        self.custom_color_row.add_suffix(self.open_picker_btn)
        self.add(self.custom_color_row)

    def _update_button_preview(self, rgba):
        """Aktualisiert die Farbe des rechteckigen Buttons."""
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(rgba.red * 255), 
            int(rgba.green * 255), 
            int(rgba.blue * 255)
        )
        provider = Gtk.CssProvider()
        # border-radius auf 6px für ein modernes Rechteck-Design
        css = f"""
            box {{ 
                background-color: {hex_color};
                border-radius: 6px;
            }}
        """
        provider.load_from_data(css.encode())
        
        self.color_preview_dot.get_style_context().add_provider(
            provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _on_open_picker(self, _btn):
        if self.picker_window and self.picker_window.get_visible():
            self.picker_window.present()
            return

        state = self.manager.get_current_state(self.serial)
        rgba = Gdk.RGBA()
        if state:
            rgba.red, rgba.green, rgba.blue = state['r']/255, state['g']/255, state['b']/255

        # Root Fenster holen
        root = self.get_native() 
        self.picker_window = ColorPickerWindow(root, rgba, self._on_color_changed_callback)
        self.picker_window.present()

    def _on_color_changed_callback(self, rgba):
        """Wird vom Picker-Fenster (Apply) aufgerufen."""
        # Hardware Update
        r, g, b = [int(c * 255) for c in [rgba.red, rgba.green, rgba.blue]]
        effect = self.get_effect_callback()
        self.manager.set_effect(effect, r, g, b, device_serial=self.serial)
        
        # UI Update (Vorschau-Button)
        self._update_button_preview(rgba)

    def _on_preset_clicked(self, _btn, rgba):
        if self.picker_window:
            self.chooser.update_rgba(rgba)
        self._on_color_changed_callback(rgba)

    def _load_initial_state(self):
        """Liest die Farbe beim Start aus und setzt die UI-Vorschau."""
        state = self.manager.get_current_state(self.serial)
        if state:
            rgba = Gdk.RGBA()
            # Umrechnung von 0-255 auf 0.0-1.0
            rgba.red = state.get('r', 255) / 255
            rgba.green = state.get('g', 255) / 255
            rgba.blue = state.get('b', 255) / 255
            rgba.alpha = 1.0
            
            # Button-Vorschau initial füllen
            self._update_button_preview(rgba)
            
            # Falls das Picker-Fenster (warum auch immer) schon existiert:
            if self.picker_window:
                self.picker_window.update_rgba(rgba)

    def _apply_preset_style(self, button, dot, hex_color):
        btn_provider = Gtk.CssProvider()
        btn_provider.load_from_data(b"button { padding: 4px; border-radius: 99px; min-width: 0; min-height: 0; }")
        button.get_style_context().add_provider(btn_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        dot_provider = Gtk.CssProvider()
        dot_provider.load_from_data(f"box {{ background-color: {hex_color}; border-radius: 99px; }}".encode())
        dot.get_style_context().add_provider(dot_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
