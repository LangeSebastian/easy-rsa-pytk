"""Certificate creation screen."""

import tkinter as tk
from ui.screens.base import MenuScreen
from ui.jogdial import JogDialNavigator
from ui.widgets import ProgressIndicator
from easyrsa.wrapper import EasyRSAWrapper
from easyrsa.pki import PKIManager
from templates.manager import TemplateManager


class CertCreateScreen(MenuScreen):
    """Certificate creation screen."""

    def __init__(self, app, navigator: JogDialNavigator):
        """Initialize certificate creation screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
        """
        super().__init__(app, navigator, title='Create Certificate')
        self.easyrsa = EasyRSAWrapper()
        self.pki_manager = PKIManager()
        self.template_manager = TemplateManager()

    def _build_menu_items(self):
        """Build certificate creation menu items."""
        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            },
            {
                'label': 'Server Certificate',
                'action': self._create_server_cert
            },
            {
                'label': 'Client Certificate',
                'action': self._create_client_cert
            },
            {
                'label': 'VPN Server Certificate',
                'action': self._create_vpn_server_cert
            },
            {
                'label': 'VPN Client Certificate',
                'action': self._create_vpn_client_cert
            }
        ]

    def _create_server_cert(self):
        """Create server certificate."""
        self._create_certificate_wizard('server', 'server')

    def _create_client_cert(self):
        """Create client certificate."""
        self._create_certificate_wizard('client', 'client')

    def _create_vpn_server_cert(self):
        """Create VPN server certificate."""
        self._create_certificate_wizard('server', 'vpn-server')

    def _create_vpn_client_cert(self):
        """Create VPN client certificate."""
        self._create_certificate_wizard('client', 'vpn-client')

    def _create_certificate_wizard(self, cert_type: str, template_name: str):
        """Start certificate creation wizard.

        Args:
            cert_type: Certificate type ('server' or 'client')
            template_name: Template name to use
        """
        # For now, use a simple text input simulation
        # In a full implementation, this would show a form screen
        self.current_cert_type = cert_type
        self.current_template = template_name

        # Show CN input screen
        self.navigator.push_screen(self)
        from ui.screens.cert_name_input import CertNameInputScreen
        input_screen = CertNameInputScreen(
            self.app,
            self.navigator,
            cert_type=cert_type,
            on_submit=self._on_cert_name_entered
        )
        self.app.show_screen(input_screen)

    def _on_cert_name_entered(self, cert_name: str):
        """Handle certificate name input.

        Args:
            cert_name: Certificate common name
        """
        if not cert_name:
            self.show_message('Error', 'Certificate name cannot be empty')
            return

        # Check if name already exists
        existing_cert = self.pki_manager.get_certificate_by_name(cert_name)
        if existing_cert:
            self.show_message('Error', f'Certificate "{cert_name}" already exists')
            return

        # Confirm and create
        if self.show_confirm('Create Certificate',
                           f'Create {self.current_cert_type} certificate:\n\n{cert_name}\n\nContinue?'):
            self._build_certificate(self.current_cert_type, cert_name, self.current_template)

    def _build_certificate(self, cert_type: str, cert_name: str, template_name: str):
        """Build the certificate.

        Args:
            cert_type: Certificate type
            cert_name: Certificate name
            template_name: Template name
        """
        self._show_progress(f'Creating {cert_type} certificate:\n{cert_name}')

        # Build certificate based on type
        if cert_type == 'server':
            result = self.easyrsa.build_server_full(cert_name, nopass=True)
        else:  # client
            result = self.easyrsa.build_client_full(cert_name, nopass=True)

        if result.success:
            cert_path = self.pki_manager.get_certificate_path(cert_name)
            key_path = self.pki_manager.get_private_key_path(cert_name)

            msg = f'Certificate created successfully!\n\n'
            msg += f'Name: {cert_name}\n'
            msg += f'Type: {cert_type}\n\n'
            msg += f'Certificate: {"✓" if cert_path else "✗"}\n'
            msg += f'Private Key: {"✓" if key_path else "✗"}'

            self.show_message('Success', msg)
        else:
            error_msg = result.stderr or result.stdout or 'Unknown error'
            self.show_message('Error', f'Failed to create certificate:\n\n{error_msg[:200]}')

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
