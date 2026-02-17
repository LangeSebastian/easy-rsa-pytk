"""USB drive detection module."""

import os
import platform
from pathlib import Path
from typing import List, Optional


class USBDetector:
    """USB drive detector for Raspberry Pi."""

    def __init__(self, mount_points: Optional[List[str]] = None):
        """Initialize USB detector.

        Args:
            mount_points: List of mount point base paths to check
        """
        from config.settings import settings

        if mount_points is None:
            mount_points = settings.usb_mount_points

        self.mount_points = mount_points
        self.system = platform.system()

    def detect_usb_drives(self) -> List[str]:
        """Detect mounted USB drives.

        Returns:
            List of USB drive mount paths
        """
        if self.system == 'Linux':
            return self._detect_linux()
        elif self.system == 'Windows':
            return self._detect_windows()
        elif self.system == 'Darwin':  # macOS
            return self._detect_macos()
        else:
            return []

    def _detect_linux(self) -> List[str]:
        """Detect USB drives on Linux.

        Returns:
            List of mount paths
        """
        drives = []

        for mount_base in self.mount_points:
            if not os.path.exists(mount_base):
                continue

            try:
                # Check subdirectories in mount base
                for entry in os.listdir(mount_base):
                    mount_path = os.path.join(mount_base, entry)

                    if os.path.ismount(mount_path) and self._is_writable(mount_path):
                        drives.append(mount_path)
            except PermissionError:
                continue

        # Also check for direct mounts
        for mount_base in self.mount_points:
            if os.path.ismount(mount_base) and self._is_writable(mount_base):
                if mount_base not in drives:
                    drives.append(mount_base)

        return drives

    def _detect_windows(self) -> List[str]:
        """Detect USB drives on Windows.

        Returns:
            List of drive letters
        """
        import string

        drives = []

        # Check all possible drive letters
        for letter in string.ascii_uppercase:
            drive_path = f'{letter}:\\'

            if os.path.exists(drive_path):
                # Check if it's a removable drive
                try:
                    # Simple heuristic: if we can write to it and it's not C:
                    if letter != 'C' and self._is_writable(drive_path):
                        drives.append(drive_path)
                except:
                    continue

        return drives

    def _detect_macos(self) -> List[str]:
        """Detect USB drives on macOS.

        Returns:
            List of mount paths
        """
        drives = []
        volumes_path = '/Volumes'

        if not os.path.exists(volumes_path):
            return drives

        try:
            for entry in os.listdir(volumes_path):
                volume_path = os.path.join(volumes_path, entry)

                # Skip Macintosh HD
                if 'Macintosh' in entry:
                    continue

                if os.path.ismount(volume_path) and self._is_writable(volume_path):
                    drives.append(volume_path)
        except PermissionError:
            pass

        return drives

    def _is_writable(self, path: str) -> bool:
        """Check if path is writable.

        Args:
            path: Path to check

        Returns:
            True if writable
        """
        try:
            test_file = os.path.join(path, '.write_test')

            # Try to write a test file
            with open(test_file, 'w') as f:
                f.write('test')

            # Remove test file
            os.remove(test_file)

            return True

        except (PermissionError, OSError):
            return False

    def get_drive_info(self, drive_path: str) -> dict:
        """Get information about a drive.

        Args:
            drive_path: Path to drive

        Returns:
            Dictionary with drive information
        """
        info = {
            'path': drive_path,
            'exists': os.path.exists(drive_path),
            'writable': self._is_writable(drive_path),
            'mount': os.path.ismount(drive_path),
            'label': os.path.basename(drive_path)
        }

        # Try to get space info
        try:
            stat = os.statvfs(drive_path) if hasattr(os, 'statvfs') else None

            if stat:
                info['total_space'] = stat.f_blocks * stat.f_frsize
                info['free_space'] = stat.f_bavail * stat.f_frsize
                info['used_space'] = info['total_space'] - info['free_space']
        except:
            pass

        return info

    def wait_for_usb(self, timeout: int = 30) -> Optional[str]:
        """Wait for a USB drive to be inserted.

        Args:
            timeout: Timeout in seconds

        Returns:
            Path to detected USB drive or None
        """
        import time

        start_time = time.time()

        while time.time() - start_time < timeout:
            drives = self.detect_usb_drives()

            if drives:
                return drives[0]

            time.sleep(1)

        return None
