"""Main menu screen."""

from ui.screens.base import MenuScreen
from ui.jogdial import JogDialNavigator


class MainMenuScreen(MenuScreen):
    """Main menu screen with primary navigation options."""

    def __init__(self, app, navigator: JogDialNavigator):
        """Initialize main menu screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
        """
        super().__init__(app, navigator, title='Easy-RSA Manager')

    def _build_menu_items(self):
        """Build main menu items."""
        self.menu_items = [
            {
                'label': 'Settings',
                'action': self._goto_settings
            },
            {
                'label': 'Certificates',
                'action': self._goto_certificates
            },
            {
                'label': 'USB Import/Export',
                'action': self._goto_usb
            },
            {
                'label': 'System Info',
                'action': self._show_system_info
            },
            {
                'label': 'About',
                'action': self._show_about
            }
        ]

    def _goto_settings(self):
        """Navigate to settings menu."""
        # Push current screen to stack
        self.navigator.push_screen(self)
        # Import here to avoid circular dependency
        from ui.screens.settings import SettingsMenuScreen
        self.app.show_screen(SettingsMenuScreen(self.app, self.navigator))

    def _goto_certificates(self):
        """Navigate to certificates menu."""
        self.navigator.push_screen(self)
        from ui.screens.certificates import CertificatesMenuScreen
        self.app.show_screen(CertificatesMenuScreen(self.app, self.navigator))

    def _goto_usb(self):
        """Navigate to USB import/export."""
        self.navigator.push_screen(self)
        from ui.screens.usb_import import USBImportExportScreen
        self.app.show_screen(USBImportExportScreen(self.app, self.navigator))

    def _show_system_info(self):
        """Show system information."""
        import platform
        import os

        info = f"""System Information

Platform: {platform.system()} {platform.release()}
Machine: {platform.machine()}
Python: {platform.python_version()}

Working Directory:
{os.getcwd()}

Display: 480x320
"""
        self.show_message('System Info', info)

    def _show_about(self):
        """Show about dialog."""
        about_text = """Easy-RSA PyTk Manager
Version 1.0

A jog-dial interface for managing
Easy-RSA certificate authority on
Raspberry Pi with 3.5" display.

Controls:
▲ UP - Navigate up
▼ DOWN - Navigate down
✓ OK - Confirm selection
"""
        self.show_message('About', about_text)
