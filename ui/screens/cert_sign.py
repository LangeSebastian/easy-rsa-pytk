"""Certificate request signing screen."""

import tkinter as tk
from ui.screens.base import MenuScreen
from ui.jogdial import JogDialNavigator
from ui.widgets import ProgressIndicator
from easyrsa.pki import PKIManager
from easyrsa.wrapper import EasyRSAWrapper


class CertSignScreen(MenuScreen):
    """Certificate signing request screen."""

    def __init__(self, app, navigator: JogDialNavigator):
        """Initialize certificate signing screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
        """
        super().__init__(app, navigator, title='Sign Certificate Request')
        self.pki_manager = PKIManager()
        self.easyrsa = EasyRSAWrapper()
        self.pending_requests = []

    def _build_menu_items(self):
        """Build certificate signing menu items."""
        self.pending_requests = self.pki_manager.list_certificate_requests()

        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            }
        ]

        if not self.pending_requests:
            self.menu_items.append({
                'label': '(No pending requests)',
                'action': lambda: self.show_message('No Requests', 'No certificate requests found.\n\nImport .req files from USB.')
            })
        else:
            for req_name in self.pending_requests:
                self.menu_items.append({
                    'label': f'📄 {req_name}',
                    'action': lambda r=req_name: self._sign_request(r)
                })

    def _sign_request(self, req_name: str):
        """Sign a certificate request.

        Args:
            req_name: Request name
        """
        # Show type selection screen
        self.navigator.push_screen(self)
        type_screen = CertTypeSelectScreen(
            self.app,
            self.navigator,
            req_name=req_name,
            on_select=self._on_type_selected
        )
        self.app.show_screen(type_screen)

    def _on_type_selected(self, req_name: str, cert_type: str):
        """Handle certificate type selection.

        Args:
            req_name: Request name
            cert_type: Certificate type ('server' or 'client')
        """
        self.show_confirm(
            'Sign Certificate',
            f'Sign certificate request:\n\n{req_name}\n\nAs: {cert_type}\n\nContinue?',
            on_yes=lambda: self._sign_certificate(req_name, cert_type)
        )

    def _sign_certificate(self, req_name: str, cert_type: str):
        """Sign the certificate.

        Args:
            req_name: Request name
            cert_type: Certificate type
        """
        self._show_progress(f'Signing certificate:\n{req_name}')

        result = self.easyrsa.sign_req(cert_type, req_name)

        if result.success:
            cert_path = self.pki_manager.get_certificate_path(req_name)
            msg = f'Certificate signed successfully!\n\n'
            msg += f'Name: {req_name}\n'
            msg += f'Type: {cert_type}\n\n'
            msg += f'Certificate: {cert_path if cert_path else "Unknown"}'
            self.show_message('Success', msg)
        else:
            error_msg = result.stderr or result.stdout or 'Unknown error'
            self.show_message('Error', f'Failed to sign certificate:\n\n{error_msg[:200]}')

    def _show_progress(self, message: str):
        """Show progress indicator.

        Args:
            message: Progress message
        """
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Show progress
        progress = ProgressIndicator(self.content_frame)
        progress.pack(fill=tk.BOTH, expand=True)
        progress.set_message(message)
        progress.set_progress(50)

        # Update display
        self.content_frame.update()


class CertTypeSelectScreen(MenuScreen):
    """Certificate type selection screen."""

    def __init__(self, app, navigator: JogDialNavigator, req_name: str, on_select=None):
        """Initialize certificate type selection screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
            req_name: Request name
            on_select: Callback when type selected
        """
        self.req_name = req_name
        self.on_select_callback = on_select
        super().__init__(app, navigator, title='Select Certificate Type')

    def _build_menu_items(self):
        """Build certificate type menu items."""
        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            },
            {
                'label': 'Server Certificate',
                'action': lambda: self._select_type('server')
            },
            {
                'label': 'Client Certificate',
                'action': lambda: self._select_type('client')
            }
        ]

    def _select_type(self, cert_type: str):
        """Handle type selection.

        Args:
            cert_type: Selected certificate type
        """
        if self.on_select_callback:
            # Go back first
            self.go_back()
            # Call callback
            self.on_select_callback(self.req_name, cert_type)
