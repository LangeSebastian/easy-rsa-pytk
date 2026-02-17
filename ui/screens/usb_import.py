"""USB import/export screen."""

from ui.screens.base import MenuScreen
from ui.jogdial import JogDialNavigator
from usb.detector import USBDetector
from usb.manager import USBFileManager
from easyrsa.pki import PKIManager
from templates.manager import TemplateManager
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
        # Rebuild menu
        self._build_menu_items()
        if self.menu_list_widget:
            menu_labels = [item['label'] for item in self.menu_items]
            self.menu_list_widget.set_items(menu_labels)
            self.navigator.set_items(self.menu_items)

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
                'label': 'Export Certificates',
                'action': self._export_certs
            },
            {
                'label': 'Drive Information',
                'action': self._show_drive_info
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
