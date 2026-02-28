from gi.repository import Gtk, Adw
from razer_control.ui.placeholder_page import PlaceholderPage
from .device_page import DevicePage

class MainWindow(Adw.Window):
    def __init__(self, app, razer_manager):
        super().__init__(application=app, title="Razer Control")
        self.razer_manager = razer_manager
        self.set_default_size(1000, 600)

        # 1. Root Layout
        self.split_view = Adw.NavigationSplitView()
        self.set_content(self.split_view)

        # 2. Sidebar Setup
        sidebar_toolbar = Adw.ToolbarView()
        sidebar_toolbar.add_top_bar(Adw.HeaderBar())

        self.device_list = Gtk.ListBox()
        self.device_list.add_css_class("navigation-sidebar")
        self.device_list.connect("row-selected", self._on_device_selected)
        
        # UI for empty sidebar state
        self._setup_sidebar_placeholder()

        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_child(self.device_list)
        sidebar_toolbar.set_content(scrolled)

        sidebar_page = Adw.NavigationPage(child=sidebar_toolbar, title="Devices")
        self.split_view.set_sidebar(sidebar_page)

        # 3. Content Setup
        self.content_toolbar = Adw.ToolbarView()
        self.content_header = Adw.HeaderBar()
        self.content_toolbar.add_top_bar(self.content_header)

        self.content_stack = Adw.ViewStack()
        self.content_toolbar.set_content(self.content_stack)

        content_page = Adw.NavigationPage(child=self.content_toolbar, title="Settings")
        self.split_view.set_content(content_page)

        self._load_devices()

    def _setup_sidebar_placeholder(self):
        """Creates a subtle label when no devices are in the list."""
        placeholder_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        placeholder_box.set_valign(Gtk.Align.CENTER)
        
        label = Gtk.Label(label="No devices")
        label.add_css_class("dim-label") # GNOME style for less important text
        
        placeholder_box.append(label)
        self.device_list.set_placeholder(placeholder_box)

    def _load_devices(self):
        """Populate UI or show placeholders."""
        if not self.razer_manager.devices:
            # Main content placeholder
            self.content_stack.add_named(PlaceholderPage(), "empty")
            self.content_stack.set_visible_child_name("empty")
            self.content_header.set_title_widget(Gtk.Label(label="Disconnected"))
            return

        # Regular device loading
        for i, dev in enumerate(self.razer_manager.devices):
            row = Adw.ActionRow(title=dev['name'])
            self.device_list.append(row)

            page = DevicePage(dev, self.razer_manager)
            self.content_stack.add_titled(page, str(i), dev['name'])

        if first := self.device_list.get_row_at_index(0):
            self.device_list.select_row(first)

    def _on_device_selected(self, listbox, row):
        if row:
            idx = str(row.get_index())
            self.content_stack.set_visible_child_name(idx)
            
            title = self.razer_manager.devices[row.get_index()]['name']
            self.content_header.set_title_widget(Gtk.Label(label=title, css_classes=["title"]))