from gi.repository import Gtk, Adw

class DefaultGroup(Adw.PreferencesGroup):
    """Verwaltet Lighting Effects und Brightness: UI, Hardware-Sync und Signale."""
    
    def __init__(self, serial, supported_effects, razer_manager, on_change_callback=None):
        super().__init__(title="Device Settings")
        self.serial = serial
        self.supported_effects = supported_effects
        self.manager = razer_manager
        self.on_change_callback = on_change_callback

        self._build_ui()
        self._connect_signals()
        self._load_initial_state()

    def _build_ui(self):
        # Effect Selection Row
        self.effect_row = Adw.ActionRow(title="Lighting Effect")
        self.dropdown = Gtk.DropDown.new_from_strings(self.supported_effects)
        self.dropdown.set_valign(Gtk.Align.CENTER)
        self.effect_row.add_suffix(self.dropdown)
        self.add(self.effect_row)

        # Brightness Row
        self.brightness_row = Adw.ActionRow(title="Brightness")
        
        # Container für Label + Scale
        brightness_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        # Wert-Anzeige (rechts)
        self.brightness_label = Gtk.Label(label="100%")
        self.brightness_label.set_size_request(40, -1) # Fixe Breite verhindert Springen der Skala

        
        # Scale: 0 bis 100
        self.brightness_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.brightness_scale.set_size_request(200, -1)
        self.brightness_scale.set_valign(Gtk.Align.CENTER)
        self.brightness_scale.set_draw_value(False) # Deaktiviert den Standard-Value oben drüber
        
        brightness_box.append(self.brightness_scale)
        brightness_box.append(self.brightness_label)
        
        self.brightness_row.add_suffix(brightness_box)
        self.add(self.brightness_row)

    def _load_initial_state(self):
        state = self.manager.get_current_state(self.serial)
        if not state:
            return

        # Effect UI Sync
        if 'effect' in state and state['effect'] in self.supported_effects:
            idx = self.supported_effects.index(state['effect'])
            self.dropdown.handler_block_by_func(self._on_effect_changed)
            self.dropdown.set_selected(idx)
            self.dropdown.handler_unblock_by_func(self._on_effect_changed)

        # Brightness UI Sync
        if 'brightness' in state:
            self.brightness_scale.handler_block_by_func(self._on_brightness_changed)
            self.brightness_scale.set_value(state['brightness'])
            self.brightness_label.set_text(f"{int(state['brightness'])}%")
            self.brightness_scale.handler_unblock_by_func(self._on_brightness_changed)

    def _connect_signals(self):
        self.dropdown.connect("notify::selected", self._on_effect_changed)
        self.brightness_scale.connect("value-changed", self._on_brightness_changed)

    def _on_effect_changed(self, *args):
        idx = self.dropdown.get_selected()
        if idx == -1: return
        
        effect = self.supported_effects[idx]
        self.manager.set_effect(effect, device_serial=self.serial)
        
        if self.on_change_callback:
            self.on_change_callback(effect)

    def _on_brightness_changed(self, scale):
        val = int(scale.get_value())
        # Setzt nur die Helligkeit, ohne den Effekt zu ändern
        self.manager.set_brightness(val, device_serial=self.serial)
        self.brightness_label.set_text(f"{val}%")

    def get_current_effect(self):
        idx = self.dropdown.get_selected()
        return self.supported_effects[idx] if idx != -1 else None