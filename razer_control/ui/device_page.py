from gi.repository import Gtk, Adw, Gdk

from razer_control.ui.components.colors_group import ColorGroup
from razer_control.ui.components.general_group import DefaultGroup

class DevicePage(Adw.Bin):
    def __init__(self, device_data, razer_manager):
        super().__init__()
        self.manager = razer_manager
        self.serial = device_data['fx']._serial
        self.supported_effects = self.manager.get_all_supported_effects(self.serial)

        self._build_ui()
        self._update_visibility() # Initialer Check nach dem Aufbau

    def _build_ui(self):
        self.clamp = Adw.Clamp(maximum_size=600)
        self.set_child(self.clamp)

        self.root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        self.clamp.set_child(self.root_box)

        # 1. General Group
        self.general_group = DefaultGroup(
            serial=self.serial,
            supported_effects=self.supported_effects,
            razer_manager=self.manager,
            on_change_callback=self._update_visibility
        )
        self.root_box.append(self.general_group)

        # 2. Color Group
        self.color_group = ColorGroup(
            serial=self.serial,
            razer_manager=self.manager,
            get_effect_callback=self.general_group.get_current_effect
        )
        self.root_box.append(self.color_group)

    def _update_visibility(self, effect=None):
        """Verwendet den übergebenen Effekt oder liest ihn aus der Gruppe."""
        if effect is None:
            if not hasattr(self, "general_group"):
                return
            effect = self.general_group.get_current_effect()
                        
        needs_color = effect in ['static', 'breathSingle', 'reactive']
        self.color_group.set_visible(needs_color)