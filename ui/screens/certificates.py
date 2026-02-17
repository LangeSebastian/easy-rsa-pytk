"""Certificates menu screen."""

from ui.screens.base import MenuScreen
from ui.jogdial import JogDialNavigator
from easyrsa.pki import PKIManager


class CertificatesMenuScreen(MenuScreen):
    """Certificates menu screen."""

    def __init__(self, app, navigator: JogDialNavigator):
        """Initialize certificates menu screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
        """
        super().__init__(app, navigator, title='Certificates')
        self.pki_manager = PKIManager()

    def _build_menu_items(self):
        """Build certificates menu items."""
        pki_info = self.pki_manager.get_pki_info()

        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            }
        ]

        # Only show cert operations if CA exists
        if pki_info.has_ca():
            self.menu_items.extend([
                {
                    'label': 'Create Certificate',
                    'action': self._create_cert
                },
                {
                    'label': 'List Certificates',
                    'action': self._list_certs
                },
                {
                    'label': 'Sign Certificate Request',
                    'action': self._sign_cert
                }
            ])
        else:
            self.menu_items.append({
                'label': '(No CA - Initialize PKI first)',
                'action': lambda: self.show_message('No CA', 'Please initialize PKI and create CA first.\n\nGo to Settings > CA Management')
            })

    def _create_cert(self):
        """Navigate to certificate creation."""
        self.navigator.push_screen(self)
        from ui.screens.cert_create import CertCreateScreen
        self.app.show_screen(CertCreateScreen(self.app, self.navigator))

    def _list_certs(self):
        """Navigate to certificate list."""
        self.navigator.push_screen(self)
        from ui.screens.cert_list import CertListScreen
        self.app.show_screen(CertListScreen(self.app, self.navigator))

    def _sign_cert(self):
        """Navigate to certificate signing."""
        self.navigator.push_screen(self)
        from ui.screens.cert_sign import CertSignScreen
        self.app.show_screen(CertSignScreen(self.app, self.navigator))
