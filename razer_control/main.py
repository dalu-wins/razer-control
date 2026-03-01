import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw
from .ui.window import MainWindow
from .core.razer_manager import RazerManager

class RazerControlApp(Adw.Application):
    """Main Application class for Razer Control."""
    
    def __init__(self):
        super().__init__(application_id='de.dalu_wins.RazerControl')
        self.razer_manager = None
        self.window = None

    def do_activate(self):
        """Initializes manager and presents the main window."""
        if not self.razer_manager:
            self.razer_manager = RazerManager()
        
        # Ensure window is only created once
        if not self.window:
            self.window = MainWindow(self, self.razer_manager)
            
        self.window.present()

def main():
    """Entry point for the application."""
    app = RazerControlApp()
    return app.run(sys.argv)