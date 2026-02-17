"""USB import/export screen."""

from ui.screens.base import MenuScreen
from ui.jogdial import JogDialNavigator
from usb.detector import USBDetector
from usb.manager import USBFileManager
from easyrsa.pki import PKIManager
from templates.manager import TemplateManager
from config.settings import settings
import os


class USBImportExportScreen(MenuScreen):
    """USB import/export main screen."""

    def __init__(self, app, navigator: JogDialNavigator):
        """Initialize USB import/export screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
        """
        super().__init__(app, navigator, title='USB Import/Export')
        self.usb_detector = USBDetector()
        self.usb_manager = USBFileManager()
        self.detected_drives = []

    def enter(self):
        """Called when screen becomes active."""
        super().enter()
        # Detect USB drives
        self.detected_drives = self.usb_detector.detect_usb_drives()

    def _build_menu_items(self):
        """Build USB menu items."""
        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            }
        ]

        # Detect USB drives
        drives = self.usb_detector.detect_usb_drives()
        self.detected_drives = drives

        if drives:
            for drive in drives:
                drive_name = os.path.basename(drive) or drive
                self.menu_items.append({
                    'label': f'💾 {drive_name}',
                    'action': lambda d=drive: self._show_drive_menu(d)
                })
        else:
            self.menu_items.append({
                'label': '(No USB drives detected)',
                'action': lambda: self.show_message('No USB', 'Please insert a USB drive')
            })

        self.menu_items.append({
            'label': 'Refresh',
            'action': self._refresh
        })

    def _refresh(self):
        """Refresh USB drive list."""
        self.app.show_screen(self)

    def _show_drive_menu(self, drive_path: str):
        """Show menu for specific USB drive.

        Args:
            drive_path: USB drive path
        """
        self.navigator.push_screen(self)
        drive_menu = USBDriveMenuScreen(self.app, self.navigator, drive_path)
        self.app.show_screen(drive_menu)


class USBDriveMenuScreen(MenuScreen):
    """USB drive operations menu."""

    def __init__(self, app, navigator: JogDialNavigator, drive_path: str):
        """Initialize USB drive menu.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
            drive_path: USB drive path
        """
        self.drive_path = drive_path
        self.usb_manager = USBFileManager()
        self.pki_manager = PKIManager()
        self.template_manager = TemplateManager()

        drive_name = os.path.basename(drive_path) or drive_path
        super().__init__(app, navigator, title=f'USB: {drive_name}')

    def _build_menu_items(self):
        """Build USB drive menu items."""
        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            },
            {
                'label': 'Import Certificate Requests',
                'action': self._import_requests
            },
            {
                'label': 'Import Templates',
                'action': self._import_templates
            },
            {
                'label': 'Import vars file',
                'action': self._import_vars
            },
            {
                'label': 'Export Certificates',
                'action': self._export_certs
            },
            {
                'label': 'Export vars file',
                'action': self._export_vars
            },
            {
                'label': 'Drive Information',
                'action': self._show_drive_info
            },
            {
                'label': 'Eject Drive',
                'action': self._eject_drive
            }
        ]

    def _import_requests(self):
        """Import certificate requests from USB."""
        # Find .req files
        req_files = self.usb_manager.list_certificate_requests(self.drive_path)

        if not req_files:
            self.show_message('No Requests', 'No .req files found on USB drive')
            return

        # Show request selection screen
        self.navigator.push_screen(self)
        select_screen = FileSelectScreen(
            self.app,
            self.navigator,
            title='Select Request to Import',
            files=req_files,
            on_select=self._on_request_selected
        )
        self.app.show_screen(select_screen)

    def _on_request_selected(self, req_file: str):
        """Handle request file selection.

        Args:
            req_file: Selected .req file path
        """
        pki_info = self.pki_manager.get_pki_info()
        req_name = self.usb_manager.import_certificate_request(req_file, pki_info.reqs_dir)

        if req_name:
            self.show_message('Success', f'Certificate request imported:\n\n{req_name}\n\nYou can now sign it from the Certificates menu.')
        else:
            self.show_message('Error', 'Failed to import certificate request')

    def _import_templates(self):
        """Import templates from USB."""
        # Find .vars files
        template_files = self.usb_manager.list_templates(self.drive_path)

        if not template_files:
            self.show_message('No Templates', 'No .vars files found on USB drive')
            return

        # Show template selection screen
        self.navigator.push_screen(self)
        select_screen = FileSelectScreen(
            self.app,
            self.navigator,
            title='Select Template to Import',
            files=template_files,
            on_select=self._on_template_selected
        )
        self.app.show_screen(select_screen)

    def _on_template_selected(self, template_file: str):
        """Handle template file selection.

        Args:
            template_file: Selected .vars file path
        """
        template_name = self.usb_manager.import_template(
            template_file,
            self.template_manager.template_dir
        )

        if template_name:
            self.show_message('Success', f'Template imported:\n\n{template_name}')
        else:
            self.show_message('Error', 'Failed to import template')

    def _export_certs(self):
        """Export certificates to USB."""
        # List available certificates
        certificates = self.pki_manager.list_certificates()

        if not certificates:
            self.show_message('No Certificates', 'No certificates to export')
            return

        # Show certificate selection
        self.navigator.push_screen(self)
        from ui.screens.cert_export import CertExportScreen
        export_screen = CertExportScreen(
            self.app,
            self.navigator,
            usb_path=self.drive_path
        )
        self.app.show_screen(export_screen)

    def _eject_drive(self):
        """Confirm and eject the USB drive."""
        drive_name = os.path.basename(self.drive_path) or self.drive_path
        self.show_confirm(
            'Eject Drive',
            f'Safely eject:\n\n{drive_name}\n\nAll operations must be finished first.',
            on_yes=self._do_eject_drive
        )

    def _do_eject_drive(self):
        """Perform the eject and navigate back to the USB list."""
        success = self.usb_manager.detector.unmount_drive(self.drive_path)

        if success:
            # Drive is gone — go back to the USB list screen and show message from there
            usb_list = self.navigator.pop_screen()
            self.app.show_screen(usb_list)
            usb_list.show_message('Ejected', 'Drive ejected safely.\n\nYou can now remove it.')
        else:
            self.show_message('Error',
                              'Failed to eject drive.\n\nClose any open files and try again.')

    def _export_vars(self):
        """Export vars file from PKI/easy-rsa directory to USB."""
        pki_info = self.pki_manager.get_pki_info()
        easyrsa_dir = os.path.dirname(settings.easyrsa_bin)

        # Look for vars in PKI dir first (easy-rsa 3.x), then easy-rsa dir
        candidates = [
            os.path.join(pki_info.pki_dir, 'vars'),
            os.path.join(easyrsa_dir, 'vars'),
            os.path.join(easyrsa_dir, 'vars.example'),
        ]

        vars_path = next((p for p in candidates if os.path.exists(p)), None)

        if not vars_path:
            self.show_message('Not Found',
                              f'No vars file found.\n\nLooked in:\n{pki_info.pki_dir}\n{easyrsa_dir}')
            return

        if self.usb_manager.export_file(vars_path, self.drive_path):
            self.show_message('Success',
                              f'Exported to USB:\n\n{os.path.basename(vars_path)}')
        else:
            self.show_message('Error', 'Failed to export vars file')

    def _import_vars(self):
        """Import a vars file from USB into the PKI directory."""
        vars_files = self.usb_manager.list_vars_files(self.drive_path)

        if not vars_files:
            self.show_message('No Files',
                              'No vars files found on USB.\n\nLooking for: vars, vars.example, *.vars')
            return

        self.navigator.push_screen(self)
        select_screen = FileSelectScreen(
            self.app,
            self.navigator,
            title='Select vars file',
            files=vars_files,
            on_select=self._on_vars_selected
        )
        self.app.show_screen(select_screen)

    def _on_vars_selected(self, vars_file: str):
        """Handle vars file selection for import.

        Args:
            vars_file: Path to selected vars file on USB
        """
        pki_info = self.pki_manager.get_pki_info()

        # Prefer PKI dir; fall back to easy-rsa dir if PKI not yet initialised
        if os.path.exists(pki_info.pki_dir):
            dest_dir = pki_info.pki_dir
        else:
            dest_dir = os.path.dirname(settings.easyrsa_bin)

        dest_path = os.path.join(dest_dir, 'vars')
        if self.usb_manager.import_file(vars_file, dest_dir, 'vars'):
            # vars file may contain secrets — restrict to owner read/write only
            try:
                os.chmod(dest_path, 0o600)
            except OSError:
                pass
            self.show_message('Success', f'vars file imported to:\n\n{dest_dir}')
        else:
            self.show_message('Error', 'Failed to import vars file')

    def _show_drive_info(self):
        """Show USB drive information."""
        info = self.usb_manager.detector.get_drive_info(self.drive_path)

        details = f"""USB Drive Information

Path: {info['path']}
Label: {info.get('label', 'Unknown')}

Status:
- Mounted: {'Yes' if info.get('mount') else 'No'}
- Writable: {'Yes' if info.get('writable') else 'No'}
"""

        if 'total_space' in info:
            total_gb = info['total_space'] / (1024**3)
            free_gb = info['free_space'] / (1024**3)
            used_gb = info['used_space'] / (1024**3)

            details += f"""
Space:
- Total: {total_gb:.2f} GB
- Used: {used_gb:.2f} GB
- Free: {free_gb:.2f} GB
"""

        self.show_message('Drive Information', details)


class FileSelectScreen(MenuScreen):
    """File selection screen for import operations."""

    def __init__(self, app, navigator: JogDialNavigator, title: str, files: list, on_select=None):
        """Initialize file select screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
            title: Screen title
            files: List of file paths
            on_select: Callback when file selected
        """
        self.files = files
        self.on_select_callback = on_select
        super().__init__(app, navigator, title=title)

    def _build_menu_items(self):
        """Build file selection menu items."""
        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            }
        ]

        for file_path in self.files:
            filename = os.path.basename(file_path)
            self.menu_items.append({
                'label': f'📄 {filename}',
                'action': lambda f=file_path: self._select_file(f)
            })

    def _select_file(self, file_path: str):
        """Handle file selection.

        Args:
            file_path: Selected file path
        """
        if self.on_select_callback:
            # Go back first
            self.go_back()
            # Call callback
            self.on_select_callback(file_path)
