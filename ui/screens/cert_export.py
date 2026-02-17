"""Certificate export screen."""

from ui.screens.base import MenuScreen
from ui.jogdial import JogDialNavigator
from easyrsa.pki import PKIManager
from usb.manager import USBFileManager
from easyrsa.models import CertificateStatus


class CertExportScreen(MenuScreen):
    """Certificate export screen."""

    def __init__(self, app, navigator: JogDialNavigator, usb_path: str):
        """Initialize certificate export screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
            usb_path: USB drive path for export
        """
        super().__init__(app, navigator, title='Export Certificates')
        self.usb_path = usb_path
        self.pki_manager = PKIManager()
        self.usb_manager = USBFileManager()

    def _build_menu_items(self):
        """Build certificate export menu items."""
        # List valid certificates only
        certificates = self.pki_manager.list_certificates(CertificateStatus.VALID)

        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            }
        ]

        if not certificates:
            self.menu_items.append({
                'label': '(No certificates to export)',
                'action': lambda: None
            })
        else:
            # Add CA certificate option
            self.menu_items.append({
                'label': '📜 CA Certificate',
                'action': self._export_ca
            })

            # Add individual certificates
            for cert in certificates:
                self.menu_items.append({
                    'label': f'📄 {cert.common_name}',
                    'action': lambda c=cert: self._export_certificate(c)
                })

    def _export_ca(self):
        """Export CA certificate."""
        ca_path = self.pki_manager.get_ca_cert_path()

        if not ca_path:
            self.show_message('Error', 'CA certificate not found')
            return

        if self.usb_manager.export_certificate(ca_path, self.usb_path):
            self.show_message('Success', f'CA certificate exported to USB')
        else:
            self.show_message('Error', 'Failed to export CA certificate')

    def _export_certificate(self, cert):
        """Export certificate.

        Args:
            cert: Certificate object
        """
        cert_path = self.pki_manager.get_certificate_path(cert.common_name)
        key_path = self.pki_manager.get_private_key_path(cert.common_name)
        ca_path = self.pki_manager.get_ca_cert_path()

        if not cert_path:
            self.show_message('Error', 'Certificate file not found')
            return

        # Ask if user wants bundle or just certificate
        if self.show_confirm('Export Options',
                           f'Export {cert.common_name}\n\nExport full bundle (cert + key + CA)?'):
            # Export bundle
            if self.usb_manager.export_certificate_bundle(
                cert_path, key_path, ca_path,
                self.usb_path, cert.common_name
            ):
                self.show_message('Success',
                                f'Certificate bundle exported:\n\n{cert.common_name}/')
            else:
                self.show_message('Error', 'Failed to export certificate bundle')
        else:
            # Export just certificate
            if self.usb_manager.export_certificate(cert_path, self.usb_path):
                self.show_message('Success', f'Certificate exported:\n\n{cert.common_name}.crt')
            else:
                self.show_message('Error', 'Failed to export certificate')
