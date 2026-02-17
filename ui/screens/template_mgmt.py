"""Template management screen."""

from ui.screens.base import MenuScreen
from ui.jogdial import JogDialNavigator
from templates.manager import TemplateManager


class TemplateManagementScreen(MenuScreen):
    """Template management screen."""

    def __init__(self, app, navigator: JogDialNavigator):
        """Initialize template management screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
        """
        super().__init__(app, navigator, title='Template Management')
        self.template_manager = TemplateManager()

    def _build_menu_items(self):
        """Build template management menu items."""
        templates = self.template_manager.list_templates()

        self.menu_items = [
            {
                'label': '← Back',
                'action': self.go_back
            }
        ]

        # List templates
        for template in templates:
            self.menu_items.append({
                'label': f'📄 {template}',
                'action': lambda t=template: self._show_template_details(t)
            })

        if not templates:
            self.menu_items.append({
                'label': '(No templates found)',
                'action': lambda: None
            })

    def _show_template_details(self, template_name: str):
        """Show template details.

        Args:
            template_name: Template name
        """
        variables = self.template_manager.load_template(template_name)

        details = f"""Template: {template_name}

Variables:
"""
        for key, value in sorted(variables.items()):
            details += f"\n{key}:\n  {value}\n"

        self.show_message(f'Template: {template_name}', details)
