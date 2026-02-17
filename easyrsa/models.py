"""Data models for easy-rsa certificates and PKI structures."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class CertificateStatus(Enum):
    """Certificate status enum."""
    VALID = 'V'
    REVOKED = 'R'
    EXPIRED = 'E'


class CertificateType(Enum):
    """Certificate type enum."""
    CA = 'ca'
    SERVER = 'server'
    CLIENT = 'client'


@dataclass
class Certificate:
    """Certificate information."""
    status: CertificateStatus
    expiration_date: datetime
    revocation_date: Optional[datetime]
    serial_number: str
    filename: str
    common_name: str
    cert_type: Optional[CertificateType] = None

    def is_valid(self) -> bool:
        """Check if certificate is valid.

        Returns:
            True if certificate is valid and not expired
        """
        if self.status != CertificateStatus.VALID:
            return False
        if self.expiration_date < datetime.now():
            return False
        return True

    def days_until_expiration(self) -> int:
        """Get days until expiration.

        Returns:
            Number of days until expiration (negative if expired)
        """
        delta = self.expiration_date - datetime.now()
        return delta.days

    def __str__(self) -> str:
        """String representation."""
        status_str = self.status.name
        if self.is_valid():
            days = self.days_until_expiration()
            status_str += f' ({days} days left)'
        return f'{self.common_name} - {status_str}'


@dataclass
class PKIInfo:
    """PKI directory information."""
    pki_dir: str
    ca_exists: bool
    ca_cert_path: Optional[str]
    ca_key_path: Optional[str]
    issued_dir: str
    private_dir: str
    reqs_dir: str
    revoked_dir: str
    index_file: str
    serial_file: str

    def is_initialized(self) -> bool:
        """Check if PKI is properly initialized.

        Returns:
            True if PKI directory structure exists
        """
        import os
        return os.path.exists(self.pki_dir) and os.path.exists(self.index_file)

    def has_ca(self) -> bool:
        """Check if CA certificate exists.

        Returns:
            True if CA certificate and key exist
        """
        import os
        if not self.ca_exists:
            return False
        if not self.ca_cert_path or not self.ca_key_path:
            return False
        return os.path.exists(self.ca_cert_path) and os.path.exists(self.ca_key_path)


@dataclass
class CommandResult:
    """Result from running an easy-rsa command."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    message: str = ''

    def __bool__(self) -> bool:
        """Boolean conversion.

        Returns:
            True if command was successful
        """
        return self.success

    def get_output(self) -> str:
        """Get combined output.

        Returns:
            Combined stdout and stderr
        """
        output = []
        if self.stdout:
            output.append(self.stdout)
        if self.stderr:
            output.append(self.stderr)
        if self.message:
            output.append(self.message)
        return '\n'.join(output)


@dataclass
class CertificateRequest:
    """Certificate signing request information."""
    name: str
    req_file: str
    common_name: Optional[str] = None
    organization: Optional[str] = None
    email: Optional[str] = None

    def __str__(self) -> str:
        """String representation."""
        return f'{self.name} ({self.common_name or "unknown CN"})'
