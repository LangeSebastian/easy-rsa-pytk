"""Certificate list and management screen."""

from ui.screens.base import MenuScreen
from ui.jogdial import JogDialNavigator
from easyrsa.pki import PKIManager
from easyrsa.wrapper import EasyRSAWrapper
from easyrsa.models import CertificateStatus
import os


class CertListScreen(MenuScreen):
    """Certificate list screen."""

    def __init__(self, app, navigator: JogDialNavigator):
        """Initialize certificate list screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
        """
        super().__init__(app, navigator, title='Certificate List')
        self.pki_manager = PKIManager()
        self.easyrsa = EasyRSAWrapper()
        self.certificates = []

    def _build_menu_items(self):
        """Build certificate list menu items."""
        self.certificates = self.pki_manager.list_certificates()

        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            }
        ]

        if not self.certificates:
            self.menu_items.append({
                'label': '(No certificates found)',
                'action': lambda: None
            })
        else:
            for cert in self.certificates:
                status_icon = '✓' if cert.status == CertificateStatus.VALID else '✗'
                label = f'{status_icon} {cert.common_name}'

                self.menu_items.append({
                    'label': label,
                    'action': lambda c=cert: self._show_cert_details(c)
                })

    def _show_cert_details(self, cert):
        """Show certificate details.

        Args:
            cert: Certificate object
        """
        # Build details screen
        self.navigator.push_screen(self)
        detail_screen = CertDetailScreen(self.app, self.navigator, cert, self.pki_manager)
        self.app.show_screen(detail_screen)


class CertDetailScreen(MenuScreen):
    """Certificate detail screen."""

    def __init__(self, app, navigator: JogDialNavigator, certificate, pki_manager):
        """Initialize certificate detail screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
            certificate: Certificate object
            pki_manager: PKI manager instance
        """
        self.certificate = certificate
        self.pki_manager = pki_manager
        self.easyrsa = EasyRSAWrapper()
        super().__init__(app, navigator, title=f'Cert: {certificate.common_name}')

    def _build_menu_items(self):
        """Build certificate detail menu items."""
        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            },
            {
                'label': 'View Details',
                'action': self._view_details
            }
        ]

        # Add actions based on status
        if self.certificate.status == CertificateStatus.VALID:
            self.menu_items.extend([
                {
                    'label': 'Export Certificate',
                    'action': self._export_cert
                },
                {
                    'label': 'Revoke Certificate',
                    'action': self._revoke_cert
                }
            ])

    def _view_details(self):
        """View certificate details."""
        cert = self.certificate
        cert_path = self.pki_manager.get_certificate_path(cert.common_name)

        details = f"""Certificate Details

Common Name: {cert.common_name}
Serial: {cert.serial_number}
Status: {cert.status.name}

Expiration: {cert.expiration_date.strftime('%Y-%m-%d %H:%M')}
Days Left: {cert.days_until_expiration()}

Certificate File:
{cert_path if cert_path else 'Not found'}

Key File:
{self.pki_manager.get_private_key_path(cert.common_name) or 'Not found'}
"""
        self.show_message('Certificate Details', details)

    def _export_cert(self):
        """Export certificate (placeholder for USB export)."""
        self.show_message('Export Certificate',
                        'USB export functionality coming in Phase 6!\n\nFor now, certificate is at:\n\n' +
                        (self.pki_manager.get_certificate_path(self.certificate.common_name) or 'Unknown'))

    def _revoke_cert(self):
        """Revoke certificate."""
        self.show_confirm(
            'Revoke Certificate',
            f'Revoke certificate:\n\n{self.certificate.common_name}\n\nThis cannot be undone!',
            on_yes=self._do_revoke_cert
        )

    def _do_revoke_cert(self):
        result = self.easyrsa.revoke(self.certificate.common_name)
        if result.success:
            crl_result = self.easyrsa.gen_crl()
            if crl_result.success:
                self.show_message('Success', 'Certificate revoked successfully.\n\nCRL updated.')
            else:
                self.show_message('Partial Success', 'Certificate revoked, but CRL generation failed.')
        else:
            error_msg = result.stderr or result.stdout or 'Unknown error'
            self.show_message('Error', f'Failed to revoke certificate:\n\n{error_msg[:200]}')
