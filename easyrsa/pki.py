"""PKI directory structure management."""

import os
from pathlib import Path
from typing import List, Optional
from easyrsa.models import PKIInfo, Certificate, CertificateStatus
from easyrsa.parser import EasyRSAParser
from config.settings import settings


class PKIManager:
    """Manager for PKI directory structure."""

    def __init__(self, pki_dir: Optional[str] = None):
        """Initialize PKI manager.

        Args:
            pki_dir: PKI directory path (default from settings)
        """
        self.pki_dir = pki_dir or settings.pki_dir

    def get_pki_info(self) -> PKIInfo:
        """Get PKI directory information.

        Returns:
            PKIInfo object with paths and status
        """
        pki_path = Path(self.pki_dir)

        # Standard easy-rsa paths
        ca_cert_path = pki_path / 'ca.crt'
        ca_key_path = pki_path / 'private' / 'ca.key'
        issued_dir = pki_path / 'issued'
        private_dir = pki_path / 'private'
        reqs_dir = pki_path / 'reqs'
        revoked_dir = pki_path / 'revoked'
        index_file = pki_path / 'index.txt'
        serial_file = pki_path / 'serial'

        return PKIInfo(
            pki_dir=str(pki_path),
            ca_exists=ca_cert_path.exists(),
            ca_cert_path=str(ca_cert_path) if ca_cert_path.exists() else None,
            ca_key_path=str(ca_key_path) if ca_key_path.exists() else None,
            issued_dir=str(issued_dir),
            private_dir=str(private_dir),
            reqs_dir=str(reqs_dir),
            revoked_dir=str(revoked_dir),
            index_file=str(index_file),
            serial_file=str(serial_file)
        )

    def is_initialized(self) -> bool:
        """Check if PKI is initialized.

        Returns:
            True if PKI directory exists
        """
        return os.path.exists(self.pki_dir)

    def has_ca(self) -> bool:
        """Check if CA exists.

        Returns:
            True if CA certificate and key exist
        """
        pki_info = self.get_pki_info()
        return pki_info.has_ca()

    def list_certificates(self, status_filter: Optional[CertificateStatus] = None) -> List[Certificate]:
        """List all certificates.

        Args:
            status_filter: Filter by status (None = all)

        Returns:
            List of Certificate objects
        """
        pki_info = self.get_pki_info()

        if not os.path.exists(pki_info.index_file):
            return []

        certificates = EasyRSAParser.parse_index_file(pki_info.index_file)

        if status_filter:
            certificates = [c for c in certificates if c.status == status_filter]

        return certificates

    def get_certificate_by_name(self, name: str) -> Optional[Certificate]:
        """Get certificate by common name.

        Args:
            name: Common name to search for

        Returns:
            Certificate object or None
        """
        certificates = self.list_certificates()

        for cert in certificates:
            if cert.common_name == name:
                return cert

        return None

    def list_certificate_requests(self) -> List[str]:
        """List pending certificate requests.

        Returns:
            List of request filenames
        """
        pki_info = self.get_pki_info()
        reqs_dir = Path(pki_info.reqs_dir)

        if not reqs_dir.exists():
            return []

        req_files = []
        for req_file in reqs_dir.glob('*.req'):
            req_files.append(req_file.stem)

        return sorted(req_files)

    def get_certificate_path(self, name: str) -> Optional[str]:
        """Get path to issued certificate file.

        Args:
            name: Certificate name

        Returns:
            Path to certificate file or None
        """
        pki_info = self.get_pki_info()
        cert_path = Path(pki_info.issued_dir) / f'{name}.crt'

        if cert_path.exists():
            return str(cert_path)

        return None

    def get_private_key_path(self, name: str) -> Optional[str]:
        """Get path to private key file.

        Args:
            name: Certificate name

        Returns:
            Path to private key file or None
        """
        pki_info = self.get_pki_info()
        key_path = Path(pki_info.private_dir) / f'{name}.key'

        if key_path.exists():
            return str(key_path)

        return None

    def get_request_path(self, name: str) -> Optional[str]:
        """Get path to certificate request file.

        Args:
            name: Request name

        Returns:
            Path to request file or None
        """
        pki_info = self.get_pki_info()
        req_path = Path(pki_info.reqs_dir) / f'{name}.req'

        if req_path.exists():
            return str(req_path)

        return None

    def get_ca_cert_path(self) -> Optional[str]:
        """Get path to CA certificate.

        Returns:
            Path to CA certificate or None
        """
        pki_info = self.get_pki_info()
        return pki_info.ca_cert_path

    def count_certificates(self) -> dict:
        """Count certificates by status.

        Returns:
            Dictionary with counts by status
        """
        certificates = self.list_certificates()

        counts = {
            'total': len(certificates),
            'valid': 0,
            'revoked': 0,
            'expired': 0
        }

        for cert in certificates:
            if cert.status == CertificateStatus.VALID:
                counts['valid'] += 1
            elif cert.status == CertificateStatus.REVOKED:
                counts['revoked'] += 1
            elif cert.status == CertificateStatus.EXPIRED:
                counts['expired'] += 1

        return counts

    def cleanup_revoked(self) -> int:
        """Move revoked certificates to revoked directory.

        Returns:
            Number of files moved
        """
        import shutil

        pki_info = self.get_pki_info()
        revoked_certs = self.list_certificates(CertificateStatus.REVOKED)

        count = 0
        for cert in revoked_certs:
            cert_path = self.get_certificate_path(cert.common_name)
            if cert_path and os.path.exists(cert_path):
                dest_path = Path(pki_info.revoked_dir) / Path(cert_path).name

                try:
                    os.makedirs(pki_info.revoked_dir, exist_ok=True)
                    shutil.move(cert_path, dest_path)
                    count += 1
                except Exception as e:
                    print(f'Error moving revoked cert: {e}')

        return count
