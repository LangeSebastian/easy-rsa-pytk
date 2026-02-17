"""Base screen class for all application screens."""

import tkinter as tk
from abc import ABC, abstractmethod
from typing import Optional, Callable
from ui.jogdial import JogDialNavigator
from config.settings import settings


class BaseScreen(ABC):
    """Abstract base class for all screens."""

    def __init__(self, app, navigator: JogDialNavigator):
        """Initialize base screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
        """
        self.app = app
        self.navigator = navigator
        self.content_frame: Optional[tk.Frame] = None
        self.is_active = False

    @abstractmethod
    def build(self, content_frame: tk.Frame):
        """Build screen UI in content frame.

        Args:
            content_frame: Frame to build UI in
        """
        pass

    def enter(self):
        """Called when screen becomes active."""
        self.is_active = True
        self._setup_navigation()

    def exit(self):
        """Called when screen becomes inactive."""
        self.is_active = False

    def refresh(self):
        """Refresh screen content."""
        pass

    def _setup_navigation(self):
        """Set up navigation callbacks for this screen."""
        self.navigator.on_selection_changed = self.on_selection_changed
        self.navigator.on_confirm = self.on_confirm

    def on_selection_changed(self, index: int, item):
        """Handle selection change.

        Args:
            index: New selection index
            item: Selected item
        """
        pass

    def on_confirm(self, index: int, item):
        """Handle confirm action.

        Args:
            index: Confirmed item index
            item: Confirmed item
        """
        pass

    def on_up(self):
        """Handle up button press."""
        self.navigator.move_up()

    def on_down(self):
        """Handle down button press."""
        self.navigator.move_down()

    def on_confirm_button(self):
        """Handle confirm button press."""
        self.navigator.confirm()

    def show_message(self, title: str, message: str):
        """Show message dialog.

        Args:
            title: Dialog title
            message: Message text
        """
        from ui.widgets import MessageBox
        MessageBox(self.content_frame, title, message, ['OK']).get_result()

    def show_confirm(self, title: str, message: str) -> bool:
        """Show confirmation dialog.

        Args:
            title: Dialog title
            message: Message text

        Returns:
            True if confirmed, False otherwise
        """
        from ui.widgets import MessageBox
        result = MessageBox(self.content_frame, title, message, ['Yes', 'No']).get_result()
        return result == 'Yes'

    def go_back(self):
        """Navigate back to previous screen."""
        previous_screen = self.navigator.pop_screen()
        if previous_screen:
            self.app.show_screen(previous_screen)


class MenuScreen(BaseScreen):
    """Base class for menu-based screens."""

    def __init__(self, app, navigator: JogDialNavigator, title: str = ''):
        """Initialize menu screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
            title: Screen title
        """
        super().__init__(app, navigator)
        self.title = title
        self.menu_items = []
        self.menu_list_widget = None

    def build(self, content_frame: tk.Frame):
        """Build menu screen UI.

        Args:
            content_frame: Frame to build UI in
        """
        self.content_frame = content_frame

        # Title bar
        if self.title:
            title_bar = tk.Frame(content_frame, bg='#2c3e50', height=40)
            title_bar.pack(fill=tk.X)
            title_bar.pack_propagate(False)

            title_label = tk.Label(
                title_bar,
                text=self.title,
                bg='#2c3e50',
                fg='white',
                font=('DejaVu Sans', settings.get('font.size_large', 12), 'bold'),
                anchor='w',
                padx=10
            )
            title_label.pack(fill=tk.BOTH, expand=True)

        # Menu list
        from ui.widgets import MenuList
        self.menu_list_widget = MenuList(content_frame, visible_items=6)
        self.menu_list_widget.pack(fill=tk.BOTH, expand=True)

        # Set menu items
        self._build_menu_items()
        menu_labels = [item['label'] for item in self.menu_items]
        self.menu_list_widget.set_items(menu_labels)
        self.navigator.set_items(self.menu_items)

    @abstractmethod
    def _build_menu_items(self):
        """Build menu items list. Override in subclass."""
        pass

    def enter(self):
        """Called when screen becomes active."""
        super().enter()
        if self.menu_list_widget:
            self.menu_list_widget.set_selection(self.navigator.get_current_index())

    def on_selection_changed(self, index: int, item):
        """Handle selection change.

        Args:
            index: New selection index
            item: Selected item
        """
        if self.menu_list_widget:
            self.menu_list_widget.set_selection(index)

    def on_confirm(self, index: int, item):
        """Handle confirm action.

        Args:
            index: Confirmed item index
            item: Confirmed item (menu item dict)
        """
        if 'action' in item and item['action']:
            item['action']()


class FormScreen(BaseScreen):
    """Base class for form-based screens."""

    def __init__(self, app, navigator: JogDialNavigator, title: str = ''):
        """Initialize form screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
            title: Screen title
        """
        super().__init__(app, navigator)
        self.title = title
        self.form_fields = []

    def build(self, content_frame: tk.Frame):
        """Build form screen UI.

        Args:
            content_frame: Frame to build UI in
        """
        self.content_frame = content_frame

        # Title bar
        if self.title:
            title_bar = tk.Frame(content_frame, bg='#2c3e50', height=40)
            title_bar.pack(fill=tk.X)
            title_bar.pack_propagate(False)

            title_label = tk.Label(
                title_bar,
                text=self.title,
                bg='#2c3e50',
                fg='white',
                font=('DejaVu Sans', settings.get('font.size_large', 12), 'bold'),
                anchor='w',
                padx=10
            )
            title_label.pack(fill=tk.BOTH, expand=True)

        # Form area
        form_area = tk.Frame(content_frame, bg='white')
        form_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_form_fields(form_area)

    @abstractmethod
    def _build_form_fields(self, parent: tk.Frame):
        """Build form fields. Override in subclass.

        Args:
            parent: Parent frame for form fields
        """
        pass
