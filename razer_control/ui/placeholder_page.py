from gi.repository import Gtk, Adw

class PlaceholderPage(Adw.Bin):
    """Displayed when no devices are detected."""
    def __init__(self):
        super().__init__()
        
        status_page = Adw.StatusPage(
            title="No Devices Found",
            description="Please ensure your Razer hardware is connected and the OpenRazer daemon is running.",
            icon_name="input-gaming-symbolic"
        )
        
        self.set_child(status_page)