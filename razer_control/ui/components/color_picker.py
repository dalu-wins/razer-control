from gi.repository import Adw, Gtk, Gdk

class ColorPickerWindow(Gtk.Window):
    def __init__(self, parent, initial_rgba, on_color_changed):
        super().__init__(title="Select Color", transient_for=parent, modal=True)
        self.set_default_size(-1, -1)
        
        self.on_color_changed = on_color_changed

        # --- HeaderBar Setup ---
        self.hb = Gtk.HeaderBar()
        
        # Back Button im Header (links)
        self.back_btn = Gtk.Button(icon_name="go-previous-symbolic")
        self.back_btn.set_visible(False)
        self.back_btn.connect("clicked", lambda _: self.chooser.set_property("show-editor", False))
        self.hb.pack_start(self.back_btn) # Packt ihn nach links
        
        self.set_titlebar(self.hb)

        # --- Content Setup ---
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.main_box.set_margin_top(12)
        self.main_box.set_margin_bottom(18)
        self.main_box.set_margin_start(18)
        self.main_box.set_margin_end(18)

        self.chooser = Gtk.ColorChooserWidget()
        self.chooser.set_use_alpha(False)
        self.chooser.set_rgba(initial_rgba)
        self.chooser.connect("notify::show-editor", self._on_show_editor_changed)
        
        # Nur noch Apply-Button unten
        self.apply_btn = Gtk.Button(label="Apply", css_classes=["suggested-action"])
        self.apply_btn.connect("clicked", self._on_apply_clicked)

        self.main_box.append(self.chooser)
        self.main_box.append(self.apply_btn)
        self.set_child(self.main_box)

    def _on_show_editor_changed(self, widget, pspec):
        is_editor = widget.get_property("show-editor")
        self.back_btn.set_visible(is_editor)
        self.set_default_size(-1, -1)
        self.present()

    def _on_apply_clicked(self, _btn):
        rgba = self.chooser.get_rgba()
        self.on_color_changed(rgba)
        self.close()

    def update_rgba(self, rgba):
        """Erlaubt das Setzen der Farbe von außen."""
        self.chooser.set_rgba(rgba)