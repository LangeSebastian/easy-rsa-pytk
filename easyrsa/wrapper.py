"""Wrapper for easy-rsa shell commands."""

import subprocess
import os
from typing import Optional
from pathlib import Path
from easyrsa.models import CommandResult
from config.settings import settings


class EasyRSAWrapper:
    """Wrapper for easy-rsa command-line tool."""

    def __init__(self, easyrsa_bin: Optional[str] = None, pki_dir: Optional[str] = None):
        """Initialize easy-rsa wrapper.

        Args:
            easyrsa_bin: Path to easyrsa binary (default from settings)
            pki_dir: PKI directory path (default from settings)
        """
        self.easyrsa_bin = easyrsa_bin or settings.easyrsa_bin
        self.pki_dir = pki_dir or settings.pki_dir
        # Set EASYRSA_PKI and EASYRSA_BATCH in process environment so they're available globally
        os.environ['EASYRSA_PKI'] = self.pki_dir
        os.environ['EASYRSA_BATCH'] = '1'

    def _run_command(self, args: list, env_vars: Optional[dict] = None) -> CommandResult:
        """Run easy-rsa command.

        Args:
            args: Command arguments
            env_vars: Additional environment variables

        Returns:
            CommandResult object
        """
        # Build command
        cmd = [self.easyrsa_bin] + args

        # Prepare environment
        env = os.environ.copy()
        env['EASYRSA_PKI'] = self.pki_dir

        if env_vars:
            env.update(env_vars)

        try:
            # Run command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60
            )

            return CommandResult(
                success=(result.returncode == 0),
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode
            )

        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                stdout='',
                stderr='Command timed out',
                exit_code=-1,
                message='Command execution timed out after 60 seconds'
            )
        except FileNotFoundError:
            return CommandResult(
                success=False,
                stdout='',
                stderr=f'easy-rsa binary not found: {self.easyrsa_bin}',
                exit_code=-1,
                message=f'Could not find easy-rsa at {self.easyrsa_bin}'
            )
        except Exception as e:
            return CommandResult(
                success=False,
                stdout='',
                stderr=str(e),
                exit_code=-1,
                message=f'Error running command: {e}'
            )

    def init_pki(self) -> CommandResult:
        """Initialize PKI directory structure.

        Returns:
            CommandResult
        """
        args = ['init-pki']
        return self._run_command(args)

    def build_ca(self, common_name: Optional[str] = None, nopass: bool = True) -> CommandResult:
        """Build Certificate Authority.

        Args:
            common_name: CA common name
            nopass: Create CA without password protection

        Returns:
            CommandResult
        """
        args = ['build-ca']

        if nopass:
            args.append('nopass')

        env_vars = {}
        if common_name:
            env_vars['EASYRSA_REQ_CN'] = common_name

        return self._run_command(args, env_vars if env_vars else None)

    def build_server_full(self, name: str, nopass: bool = True) -> CommandResult:
        """Build server certificate with key.

        Args:
            name: Server certificate name
            nopass: Create without password protection

        Returns:
            CommandResult
        """
        args = ['build-server-full', name]

        if nopass:
            args.append('nopass')

        return self._run_command(args)

    def build_client_full(self, name: str, nopass: bool = True) -> CommandResult:
        """Build client certificate with key.

        Args:
            name: Client certificate name
            nopass: Create without password protection

        Returns:
            CommandResult
        """
        args = ['build-client-full', name]

        if nopass:
            args.append('nopass')

        return self._run_command(args)

    def gen_req(self, name: str, nopass: bool = True) -> CommandResult:
        """Generate certificate request (without signing).

        Args:
            name: Certificate request name
            nopass: Create without password protection

        Returns:
            CommandResult
        """
        args = ['gen-req', name]

        if nopass:
            args.append('nopass')

        return self._run_command(args)

    def import_req(self, req_file: str, short_name: str) -> CommandResult:
        """Import certificate request.

        Args:
            req_file: Path to .req file
            short_name: Short name for the request

        Returns:
            CommandResult
        """
        args = ['import-req', req_file, short_name]
        return self._run_command(args)

    def sign_req(self, cert_type: str, name: str) -> CommandResult:
        """Sign certificate request.

        Args:
            cert_type: Certificate type ('server' or 'client')
            name: Certificate name to sign

        Returns:
            CommandResult
        """
        args = ['sign-req', cert_type, name]
        return self._run_command(args)

    def revoke(self, name: str, reason: str = 'unspecified') -> CommandResult:
        """Revoke certificate.

        Args:
            name: Certificate name to revoke
            reason: Revocation reason

        Returns:
            CommandResult
        """
        args = ['revoke', name]
        return self._run_command(args)

    def gen_crl(self) -> CommandResult:
        """Generate Certificate Revocation List.

        Returns:
            CommandResult
        """
        args = ['gen-crl']
        return self._run_command(args)

    def show_cert(self, name: str) -> CommandResult:
        """Show certificate details.

        Args:
            name: Certificate name

        Returns:
            CommandResult
        """
        args = ['show-cert', name]
        return self._run_command(args)

    def set_vars(self, vars_file: str) -> dict:
        """Load variables from vars file.

        Args:
            vars_file: Path to vars file

        Returns:
            Dictionary of environment variables
        """
        env_vars = {}

        if not os.path.exists(vars_file):
            return env_vars

        try:
            with open(vars_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Parse set_var lines
                    if line.startswith('set_var '):
                        parts = line[8:].split(None, 1)
                        if len(parts) == 2:
                            key = parts[0]
                            value = parts[1].strip('"\'')
                            env_vars[key] = value
                    # Parse export lines
                    elif line.startswith('export '):
                        parts = line[7:].split('=', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip('"\'')
                            env_vars[key] = value

        except Exception as e:
            print(f'Error loading vars file: {e}')

        return env_vars
