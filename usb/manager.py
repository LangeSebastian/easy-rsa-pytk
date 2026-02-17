"""USB file manager for import/export operations."""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from usb.detector import USBDetector


class USBFileManager:
    """Manager for USB file operations."""

    def __init__(self):
        """Initialize USB file manager."""
        self.detector = USBDetector()

    def list_files(self, usb_path: str, pattern: str = '*') -> List[str]:
        """List files on USB drive.

        Args:
            usb_path: USB drive path
            pattern: File pattern to match (e.g., '*.req', '*.crt')

        Returns:
            List of file paths
        """
        if not os.path.exists(usb_path):
            return []

        try:
            path = Path(usb_path)
            files = []

            # Search recursively for matching files
            for file_path in path.rglob(pattern):
                if file_path.is_file():
                    files.append(str(file_path))

            return sorted(files)

        except PermissionError:
            return []

    def import_file(self, source_path: str, dest_dir: str, filename: Optional[str] = None) -> bool:
        """Import file from USB to local directory.

        Args:
            source_path: Source file path on USB
            dest_dir: Destination directory
            filename: Optional new filename (default: keep original)

        Returns:
            True if imported successfully
        """
        if not os.path.exists(source_path):
            return False

        try:
            # Create destination directory if needed
            os.makedirs(dest_dir, exist_ok=True)

            # Determine destination filename
            if filename is None:
                filename = os.path.basename(source_path)

            dest_path = os.path.join(dest_dir, filename)

            # Copy file
            shutil.copy2(source_path, dest_path)

            return True

        except Exception as e:
            print(f'Error importing file: {e}')
            return False

    def export_file(self, source_path: str, usb_path: str, filename: Optional[str] = None) -> bool:
        """Export file to USB drive.

        Args:
            source_path: Source file path
            usb_path: USB drive path
            filename: Optional new filename (default: keep original)

        Returns:
            True if exported successfully
        """
        if not os.path.exists(source_path):
            return False

        if not os.path.exists(usb_path):
            return False

        try:
            # Determine destination filename
            if filename is None:
                filename = os.path.basename(source_path)

            dest_path = os.path.join(usb_path, filename)

            # Copy file
            shutil.copy2(source_path, dest_path)

            return True

        except Exception as e:
            print(f'Error exporting file: {e}')
            return False

    def import_certificate_request(self, req_file: str, pki_reqs_dir: str) -> Optional[str]:
        """Import certificate request file.

        Args:
            req_file: Path to .req file on USB
            pki_reqs_dir: PKI reqs directory

        Returns:
            Name of imported request or None
        """
        if not req_file.endswith('.req'):
            return None

        req_name = Path(req_file).stem

        if self.import_file(req_file, pki_reqs_dir):
            return req_name

        return None

    def export_certificate(self, cert_path: str, usb_path: str) -> bool:
        """Export certificate to USB.

        Args:
            cert_path: Path to certificate file
            usb_path: USB drive path

        Returns:
            True if exported successfully
        """
        return self.export_file(cert_path, usb_path)

    def export_certificate_bundle(self, cert_path: str, key_path: str, ca_path: str,
                                  usb_path: str, bundle_name: str) -> bool:
        """Export certificate bundle (cert + key + CA).

        Args:
            cert_path: Path to certificate
            key_path: Path to private key
            ca_path: Path to CA certificate
            usb_path: USB drive path
            bundle_name: Base name for bundle

        Returns:
            True if all files exported
        """
        success = True

        # Create bundle directory on USB
        bundle_dir = os.path.join(usb_path, bundle_name)

        try:
            os.makedirs(bundle_dir, exist_ok=True)
        except:
            return False

        # Export certificate
        if cert_path and os.path.exists(cert_path):
            success &= self.export_file(cert_path, bundle_dir, f'{bundle_name}.crt')

        # Export key
        if key_path and os.path.exists(key_path):
            success &= self.export_file(key_path, bundle_dir, f'{bundle_name}.key')

        # Export CA cert
        if ca_path and os.path.exists(ca_path):
            success &= self.export_file(ca_path, bundle_dir, 'ca.crt')

        return success

    def import_template(self, vars_file: str, template_dir: str) -> Optional[str]:
        """Import template vars file.

        Args:
            vars_file: Path to .vars file on USB
            template_dir: Template directory

        Returns:
            Name of imported template or None
        """
        if not vars_file.endswith('.vars'):
            return None

        template_name = Path(vars_file).stem

        if self.import_file(vars_file, template_dir):
            return template_name

        return None

    def list_certificate_requests(self, usb_path: str) -> List[str]:
        """List certificate request files on USB.

        Args:
            usb_path: USB drive path

        Returns:
            List of .req file paths
        """
        return self.list_files(usb_path, '*.req')

    def list_templates(self, usb_path: str) -> List[str]:
        """List template files on USB.

        Args:
            usb_path: USB drive path

        Returns:
            List of .vars file paths
        """
        return self.list_files(usb_path, '*.vars')

    def get_file_info(self, file_path: str) -> dict:
        """Get file information.

        Args:
            file_path: Path to file

        Returns:
            Dictionary with file information
        """
        info = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'exists': os.path.exists(file_path),
            'size': 0,
            'modified': None
        }

        if os.path.exists(file_path):
            stat = os.stat(file_path)
            info['size'] = stat.st_size
            info['modified'] = stat.st_mtime

        return info
