"""Settings menu screen."""

from ui.screens.base import MenuScreen
from ui.jogdial import JogDialNavigator
from easyrsa.pki import PKIManager
from config.settings import settings
import platform
import os


class SettingsMenuScreen(MenuScreen):
    """Settings menu screen."""

    def __init__(self, app, navigator: JogDialNavigator):
        """Initialize settings menu screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
        """
        super().__init__(app, navigator, title='Settings')
        self.pki_manager = PKIManager()

    def _build_menu_items(self):
        """Build settings menu items."""
        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            },
            {
                'label': 'CA Management',
                'action': self._goto_ca_init
            },
            {
                'label': 'PKI Settings',
                'action': self._show_pki_settings
            },
            {
                'label': 'Template Management',
                'action': self._goto_templates
            },
            {
                'label': 'System Information',
                'action': self._show_system_info
            }
        ]

    def _goto_ca_init(self):
        """Navigate to CA initialization screen."""
        self.navigator.push_screen(self)
        from ui.screens.ca_init import CAInitScreen
        self.app.show_screen(CAInitScreen(self.app, self.navigator))

    def _show_pki_settings(self):
        """Show PKI settings."""
        pki_info = self.pki_manager.get_pki_info()

        info = f"""PKI Configuration

PKI Directory:
{pki_info.pki_dir}

Status:
{'✓ Initialized' if pki_info.is_initialized() else '✗ Not initialized'}

CA Status:
{'✓ CA exists' if pki_info.has_ca() else '✗ No CA'}

Paths:
- Issued: {os.path.basename(pki_info.issued_dir)}
- Private: {os.path.basename(pki_info.private_dir)}
- Requests: {os.path.basename(pki_info.reqs_dir)}

Easy-RSA Binary:
{settings.easyrsa_bin}
"""
        self.show_message('PKI Settings', info)

    def _goto_templates(self):
        """Navigate to template management."""
        self.navigator.push_screen(self)
        from ui.screens.template_mgmt import TemplateManagementScreen
        self.app.show_screen(TemplateManagementScreen(self.app, self.navigator))

    def _show_system_info(self):
        """Show system information."""
        pki_info = self.pki_manager.get_pki_info()
        cert_counts = self.pki_manager.count_certificates()

        info = f"""System Information

Platform: {platform.system()}
Release: {platform.release()}
Machine: {platform.machine()}
Python: {platform.python_version()}

Application:
Version: 1.0
Display: {settings.window_width}x{settings.window_height}

PKI Status:
- Initialized: {'Yes' if pki_info.is_initialized() else 'No'}
- CA Present: {'Yes' if pki_info.has_ca() else 'No'}
- Total Certs: {cert_counts['total']}
- Valid Certs: {cert_counts['valid']}

Working Directory:
{os.getcwd()}
"""
        self.show_message('System Information', info)
