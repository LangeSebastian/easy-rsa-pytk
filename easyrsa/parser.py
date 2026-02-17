"""Parser for easy-rsa output and index files."""

import re
from datetime import datetime
from typing import List, Optional, Dict
from easyrsa.models import Certificate, CertificateStatus, CertificateType


class EasyRSAParser:
    """Parser for easy-rsa output and files."""

    @staticmethod
    def parse_index_line(line: str) -> Optional[Certificate]:
        """Parse a line from index.txt file.

        Format: status expiry_date revocation_date serial filename DN

        Args:
            line: Line from index.txt

        Returns:
            Certificate object or None if parse fails
        """
        line = line.strip()
        if not line or line.startswith('#'):
            return None

        parts = line.split('\t')
        if len(parts) < 5:
            return None

        try:
            # Status
            status_char = parts[0]
            if status_char == 'V':
                status = CertificateStatus.VALID
            elif status_char == 'R':
                status = CertificateStatus.REVOKED
            elif status_char == 'E':
                status = CertificateStatus.EXPIRED
            else:
                return None

            # Expiration date (format: YYMMDDHHmmssZ)
            exp_str = parts[1]
            expiration_date = datetime.strptime(exp_str, '%y%m%d%H%M%SZ')

            # Revocation date (may be empty)
            rev_date_str = parts[2]
            revocation_date = None
            if rev_date_str:
                revocation_date = datetime.strptime(rev_date_str, '%y%m%d%H%M%SZ')

            # Serial number
            serial_number = parts[3]

            # Filename
            filename = parts[4] if len(parts) > 4 else 'unknown'

            # DN (Distinguished Name)
            dn = parts[5] if len(parts) > 5 else ''

            # Extract CN from DN
            common_name = EasyRSAParser.extract_cn_from_dn(dn)

            return Certificate(
                status=status,
                expiration_date=expiration_date,
                revocation_date=revocation_date,
                serial_number=serial_number,
                filename=filename,
                common_name=common_name
            )

        except Exception as e:
            print(f'Error parsing index line: {e}')
            return None

    @staticmethod
    def parse_index_file(index_path: str) -> List[Certificate]:
        """Parse entire index.txt file.

        Args:
            index_path: Path to index.txt file

        Returns:
            List of Certificate objects
        """
        certificates = []

        try:
            with open(index_path, 'r') as f:
                for line in f:
                    cert = EasyRSAParser.parse_index_line(line)
                    if cert:
                        certificates.append(cert)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f'Error reading index file: {e}')

        return certificates

    @staticmethod
    def extract_cn_from_dn(dn: str) -> str:
        """Extract Common Name from Distinguished Name.

        Args:
            dn: Distinguished name string (e.g., "/CN=server1/O=MyOrg")

        Returns:
            Common name or empty string
        """
        # Match CN=value
        match = re.search(r'/CN=([^/]+)', dn)
        if match:
            return match.group(1)

        # Alternative format
        match = re.search(r'CN\s*=\s*([^,]+)', dn)
        if match:
            return match.group(1).strip()

        return ''

    @staticmethod
    def parse_cert_details(output: str) -> Dict[str, str]:
        """Parse certificate details from show-cert output.

        Args:
            output: Output from show-cert command

        Returns:
            Dictionary of certificate details
        """
        details = {}

        # Extract subject
        subject_match = re.search(r'Subject:(.+?)(?:\n|$)', output)
        if subject_match:
            details['subject'] = subject_match.group(1).strip()

        # Extract issuer
        issuer_match = re.search(r'Issuer:(.+?)(?:\n|$)', output)
        if issuer_match:
            details['issuer'] = issuer_match.group(1).strip()

        # Extract validity dates
        not_before_match = re.search(r'Not Before:\s*(.+?)(?:\n|$)', output)
        if not_before_match:
            details['not_before'] = not_before_match.group(1).strip()

        not_after_match = re.search(r'Not After\s*:\s*(.+?)(?:\n|$)', output)
        if not_after_match:
            details['not_after'] = not_after_match.group(1).strip()

        # Extract serial
        serial_match = re.search(r'Serial Number:\s*([0-9a-fA-F:]+)', output)
        if serial_match:
            details['serial'] = serial_match.group(1).strip()

        # Extract key algorithm
        key_match = re.search(r'Public Key Algorithm:\s*(.+?)(?:\n|$)', output)
        if key_match:
            details['key_algorithm'] = key_match.group(1).strip()

        return details

    @staticmethod
    def detect_cert_type(cert_path: str) -> CertificateType:
        """Detect certificate type from file.

        Args:
            cert_path: Path to certificate file

        Returns:
            Certificate type
        """
        # Simple heuristic based on filename
        filename = cert_path.lower()

        if 'ca' in filename:
            return CertificateType.CA
        elif 'server' in filename:
            return CertificateType.SERVER
        elif 'client' in filename:
            return CertificateType.CLIENT

        # Try to detect from certificate extensions
        try:
            import subprocess
            result = subprocess.run(
                ['openssl', 'x509', '-in', cert_path, '-noout', '-ext', 'keyUsage,extendedKeyUsage'],
                capture_output=True,
                text=True,
                timeout=5
            )

            output = result.stdout.lower()

            if 'tls web server' in output:
                return CertificateType.SERVER
            elif 'tls web client' in output:
                return CertificateType.CLIENT
            elif 'certificate sign' in output:
                return CertificateType.CA

        except Exception:
            pass

        # Default to client
        return CertificateType.CLIENT

    @staticmethod
    def parse_error_message(stderr: str) -> str:
        """Parse and simplify error messages from easy-rsa.

        Args:
            stderr: Error output from command

        Returns:
            Simplified error message
        """
        if not stderr:
            return 'Unknown error occurred'

        # Remove technical details and keep user-friendly messages
        lines = stderr.split('\n')
        error_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip debug/technical lines
            if line.startswith('[') or line.startswith('*'):
                continue

            # Keep error lines
            if 'error' in line.lower() or 'failed' in line.lower():
                error_lines.append(line)

        if error_lines:
            return '\n'.join(error_lines[:3])

        # Return first non-empty lines
        non_empty = [l for l in lines if l.strip()]
        if non_empty:
            return '\n'.join(non_empty[:3])

        return stderr[:200]
