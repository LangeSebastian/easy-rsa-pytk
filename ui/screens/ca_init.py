"""CA initialization screen."""

import tkinter as tk
from ui.screens.base import MenuScreen
from ui.jogdial import JogDialNavigator
from ui.widgets import InfoPanel, ProgressIndicator
from easyrsa.wrapper import EasyRSAWrapper
from easyrsa.pki import PKIManager
from templates.manager import TemplateManager
from config.settings import settings


class CAInitScreen(MenuScreen):
    """CA initialization wizard screen."""

    def __init__(self, app, navigator: JogDialNavigator):
        """Initialize CA init screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
        """
        super().__init__(app, navigator, title='Initialize CA')
        self.easyrsa = EasyRSAWrapper()
        self.pki_manager = PKIManager()
        self.template_manager = TemplateManager()
        self.selected_template = None

    def _build_menu_items(self):
        """Build CA initialization menu items."""
        pki_info = self.pki_manager.get_pki_info()

        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            }
        ]

        # Check if PKI exists
        if pki_info.is_initialized():
            if pki_info.has_ca():
                self.menu_items.extend([
                    {
                        'label': 'CA Status',
                        'action': self._show_ca_status
                    },
                    {
                        'label': 'Reinitialize PKI (DANGER)',
                        'action': self._reinit_pki
                    }
                ])
            else:
                self.menu_items.extend([
                    {
                        'label': 'Build CA',
                        'action': self._build_ca_wizard
                    },
                    {
                        'label': 'Reinitialize PKI',
                        'action': self._reinit_pki
                    }
                ])
        else:
            self.menu_items.append({
                'label': 'Initialize PKI',
                'action': self._init_pki
            })

    def _show_ca_status(self):
        """Show CA status information."""
        pki_info = self.pki_manager.get_pki_info()
        cert_counts = self.pki_manager.count_certificates()

        status = f"""CA Status

PKI Directory: {pki_info.pki_dir}

CA Certificate: {'✓ Exists' if pki_info.has_ca() else '✗ Not found'}

Certificates:
- Total: {cert_counts['total']}
- Valid: {cert_counts['valid']}
- Revoked: {cert_counts['revoked']}
- Expired: {cert_counts['expired']}
"""
        self.show_message('CA Status', status)

    def _init_pki(self):
        """Initialize PKI directory."""
        self.show_confirm(
            'Initialize PKI',
            'This will create a new PKI directory structure.\n\nContinue?',
            on_yes=self._do_init_pki
        )

    def _do_init_pki(self):
        self._show_progress('Initializing PKI...')
        result = self.easyrsa.init_pki()
        if result.success:
            self.show_message('Success', 'PKI initialized successfully!\n\nYou can now build the CA.')
        else:
            self.show_message('Error', f'Failed to initialize PKI:\n\n{result.stderr}')

    def _reinit_pki(self):
        """Reinitialize PKI (destroys existing)."""
        self.show_confirm(
            'Reinitialize PKI',
            'WARNING: This will DELETE all existing certificates and keys!\n\nAre you sure?',
            on_yes=self._confirm_reinit_step2
        )

    def _confirm_reinit_step2(self):
        self.show_confirm(
            'Confirm Deletion',
            'This action cannot be undone.\n\nReally delete everything?',
            on_yes=self._do_reinit_pki
        )

    def _do_reinit_pki(self):
        self._show_progress('Reinitializing PKI...')
        result = self.easyrsa.init_pki(force=True)
        if result.success:
            self.show_message('Success', 'PKI reinitialized.\n\nYou can now build a new CA.')
        else:
            self.show_message('Error', f'Failed to reinitialize PKI:\n\n{result.stderr}')

    def _build_ca_wizard(self):
        """Start CA build wizard."""
        # Show template selection screen
        self.navigator.push_screen(self)
        from ui.screens.template_select import TemplateSelectScreen
        template_screen = TemplateSelectScreen(
            self.app,
            self.navigator,
            template_type='ca',
            on_select=self._on_template_selected
        )
        self.app.show_screen(template_screen)

    def _on_template_selected(self, template_name: str):
        """Handle template selection.

        Args:
            template_name: Selected template name
        """
        self.selected_template = template_name

        # Load template to get CN
        template_vars = self.template_manager.load_template(template_name)
        ca_cn = template_vars.get('EASYRSA_REQ_CN', 'Easy-RSA CA')

        self.show_confirm(
            'Build CA',
            f'Build CA with:\n\nTemplate: {template_name}\nCN: {ca_cn}\n\nContinue?',
            on_yes=lambda: self._build_ca(template_name, ca_cn)
        )

    def _build_ca(self, template_name: str, ca_cn: str):
        """Build the CA.

        Args:
            template_name: Template to use
            ca_cn: CA common name
        """
        self._show_progress(f'Building CA: {ca_cn}...')

        # Build CA
        result = self.easyrsa.build_ca(common_name=ca_cn, nopass=True)

        if result.success:
            self.show_message('Success',
                            f'CA created successfully!\n\nCommon Name: {ca_cn}\n\nYou can now create certificates.')
        else:
            error_msg = result.stderr or result.stdout or 'Unknown error'
            self.show_message('Error', f'Failed to build CA:\n\n{error_msg[:200]}')

    def _show_progress(self, message: str):
        """Show progress indicator.

        Args:
            message: Progress message
        """
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Show progress
        progress = ProgressIndicator(self.content_frame)
        progress.pack(fill=tk.BOTH, expand=True)
        progress.set_message(message)
        progress.set_progress(50)

        # Update display
        self.content_frame.update()


class TemplateSelectScreen(MenuScreen):
    """Template selection screen."""

    def __init__(self, app, navigator: JogDialNavigator, template_type: str = 'ca', on_select=None):
        """Initialize template select screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
            template_type: Type filter for templates
            on_select: Callback when template selected
        """
        self.template_type = template_type
        self.on_select_callback = on_select
        self.template_manager = TemplateManager()
        super().__init__(app, navigator, title=f'Select {template_type.upper()} Template')

    def _build_menu_items(self):
        """Build template selection menu."""
        templates = self.template_manager.list_templates()

        # Filter by type if specified
        if self.template_type:
            templates = [t for t in templates if self.template_type.lower() in t.lower()]

        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            }
        ]

        for template in templates:
            self.menu_items.append({
                'label': template,
                'action': lambda t=template: self._select_template(t)
            })

        if len(self.menu_items) == 1:
            self.menu_items.append({
                'label': '(No templates found)',
                'action': lambda: None
            })

    def _select_template(self, template_name: str):
        """Handle template selection.

        Args:
            template_name: Selected template
        """
        if self.on_select_callback:
            # Go back first
            self.go_back()
            # Call callback
            self.on_select_callback(template_name)
