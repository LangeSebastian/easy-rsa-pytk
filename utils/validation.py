"""Input validation utilities."""

import re
from typing import Optional


def validate_certificate_name(name: str) -> tuple[bool, Optional[str]]:
    """Validate certificate name.

    Args:
        name: Certificate name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, 'Certificate name cannot be empty'

    if len(name) < 1:
        return False, 'Certificate name too short'

    if len(name) > 64:
        return False, 'Certificate name too long (max 64 characters)'

    # Allow alphanumeric, hyphen, underscore, dot
    if not re.match(r'^[a-zA-Z0-9._-]+$', name):
        return False, 'Certificate name can only contain letters, numbers, dots, hyphens, and underscores'

    # Cannot start with dot or hyphen
    if name[0] in '.-':
        return False, 'Certificate name cannot start with dot or hyphen'

    return True, None


def validate_common_name(cn: str) -> tuple[bool, Optional[str]]:
    """Validate common name.

    Args:
        cn: Common name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not cn:
        return False, 'Common name cannot be empty'

    if len(cn) > 64:
        return False, 'Common name too long (max 64 characters)'

    # More permissive than certificate names
    if not re.match(r'^[a-zA-Z0-9 ._-]+$', cn):
        return False, 'Common name contains invalid characters'

    return True, None


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """Validate email address.

    Args:
        email: Email to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return True, None  # Email is optional

    # Simple email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, 'Invalid email format'

    return True, None


def validate_key_size(key_size: int) -> tuple[bool, Optional[str]]:
    """Validate RSA key size.

    Args:
        key_size: Key size in bits

    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_sizes = [1024, 2048, 4096, 8192]

    if key_size not in valid_sizes:
        return False, f'Invalid key size (must be one of {valid_sizes})'

    if key_size < 2048:
        return True, 'Warning: Key size < 2048 is not recommended for security'

    return True, None


def validate_days(days: int, max_days: int = 10950) -> tuple[bool, Optional[str]]:
    """Validate certificate validity period.

    Args:
        days: Validity period in days
        max_days: Maximum allowed days (default 30 years)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if days < 1:
        return False, 'Validity period must be at least 1 day'

    if days > max_days:
        return False, f'Validity period cannot exceed {max_days} days'

    if days > 825:  # More than ~2 years
        return True, 'Warning: Validity period > 825 days may not be accepted by some browsers'

    return True, None


def validate_file_path(path: str, must_exist: bool = False) -> tuple[bool, Optional[str]]:
    """Validate file path.

    Args:
        path: File path to validate
        must_exist: Whether file must exist

    Returns:
        Tuple of (is_valid, error_message)
    """
    import os

    if not path:
        return False, 'Path cannot be empty'

    if must_exist and not os.path.exists(path):
        return False, 'File does not exist'

    # Check for path traversal
    if '..' in path:
        return False, 'Path cannot contain ".."'

    return True, None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')

    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"|?*]', '', filename)

    # Replace multiple spaces/dots with single
    filename = re.sub(r'[.\s]+', '.', filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')

    # Ensure not empty
    if not filename:
        filename = 'unnamed'

    return filename


def validate_template_name(name: str) -> tuple[bool, Optional[str]]:
    """Validate template name.

    Args:
        name: Template name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, 'Template name cannot be empty'

    if len(name) > 32:
        return False, 'Template name too long (max 32 characters)'

    # Alphanumeric, hyphen, underscore only
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        return False, 'Template name can only contain letters, numbers, hyphens, and underscores'

    return True, None
