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
        self.navigator.on_selection_changed = None
        self.navigator.on_confirm = None

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
        """Show an info screen in the content area. OK goes back.

        Args:
            title: Screen title
            message: Message text
        """
        self.navigator.push_screen(self)
        self.app.show_screen(InfoScreen(self.app, self.navigator, title, message))

    def show_confirm(self, title: str, message: str, on_yes=None, on_no=None):
        """Show a confirmation screen with Yes/No menu. Callbacks are invoked after selection.

        Args:
            title: Screen title
            message: Question/warning text
            on_yes: Callable invoked when user selects Yes
            on_no: Callable invoked when user selects No
        """
        self.navigator.push_screen(self)
        self.app.show_screen(ConfirmScreen(self.app, self.navigator, title, message, on_yes, on_no))

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


class InfoScreen(BaseScreen):
    """Displays a title and scrollable message. OK goes back."""

    def __init__(self, app, navigator: JogDialNavigator, title: str, message: str):
        super().__init__(app, navigator)
        self.title = title
        self.message = message
        self._text_widget = None

    def build(self, content_frame: tk.Frame):
        self.content_frame = content_frame

        if self.title:
            title_bar = tk.Frame(content_frame, bg='#2c3e50', height=40)
            title_bar.pack(fill=tk.X)
            title_bar.pack_propagate(False)
            tk.Label(
                title_bar, text=self.title,
                bg='#2c3e50', fg='white',
                font=('DejaVu Sans', settings.get('font.size_large', 12), 'bold'),
                anchor='w', padx=10
            ).pack(fill=tk.BOTH, expand=True)

        hint_bar = tk.Frame(content_frame, bg='#27ae60', height=28)
        hint_bar.pack(fill=tk.X, side=tk.BOTTOM)
        hint_bar.pack_propagate(False)
        tk.Label(
            hint_bar, text='OK \u2192 Back',
            bg='#27ae60', fg='white',
            font=('DejaVu Sans', settings.get('font.size_small', 8), 'bold'),
            anchor='center'
        ).pack(fill=tk.BOTH, expand=True)

        self._text_widget = tk.Text(
            content_frame,
            wrap=tk.WORD,
            bg='white', fg='#2c3e50',
            font=('DejaVu Sans', settings.get('font.size_normal', 10)),
            padx=10, pady=8,
            relief=tk.FLAT, highlightthickness=0
        )
        self._text_widget.insert(1.0, self.message)
        self._text_widget.config(state=tk.DISABLED)
        self._text_widget.pack(fill=tk.BOTH, expand=True)

    def on_up(self):
        if self._text_widget:
            self._text_widget.yview_scroll(-1, 'units')

    def on_down(self):
        if self._text_widget:
            self._text_widget.yview_scroll(1, 'units')

    def on_confirm_button(self):
        self.go_back()


class ConfirmScreen(MenuScreen):
    """Displays a message with Yes/No menu. Callbacks are invoked after selection."""

    def __init__(self, app, navigator: JogDialNavigator, title: str, message: str,
                 on_yes=None, on_no=None):
        super().__init__(app, navigator, title=title)
        self.message = message
        self.on_yes_callback = on_yes
        self.on_no_callback = on_no

    def build(self, content_frame: tk.Frame):
        self.content_frame = content_frame

        if self.title:
            title_bar = tk.Frame(content_frame, bg='#e67e22', height=40)
            title_bar.pack(fill=tk.X)
            title_bar.pack_propagate(False)
            tk.Label(
                title_bar, text=self.title,
                bg='#e67e22', fg='white',
                font=('DejaVu Sans', settings.get('font.size_large', 12), 'bold'),
                anchor='w', padx=10
            ).pack(fill=tk.BOTH, expand=True)

        msg_frame = tk.Frame(content_frame, bg='#fef9e7')
        msg_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(
            msg_frame, text=self.message,
            bg='#fef9e7', fg='#2c3e50',
            font=('DejaVu Sans', settings.get('font.size_normal', 10)),
            anchor='nw', padx=10, pady=8,
            justify=tk.LEFT, wraplength=340
        ).pack(fill=tk.BOTH, expand=True)

        from ui.widgets import MenuList
        self.menu_list_widget = MenuList(content_frame, visible_items=2)
        self.menu_list_widget.pack(fill=tk.X)

        self._build_menu_items()
        menu_labels = [item['label'] for item in self.menu_items]
        self.menu_list_widget.set_items(menu_labels)
        self.navigator.set_items(self.menu_items)

    def _build_menu_items(self):
        self.menu_items = [
            {'label': 'Yes', 'action': self._on_yes},
            {'label': 'No',  'action': self._on_no},
        ]

    def _on_yes(self):
        self.go_back()
        if self.on_yes_callback:
            self.on_yes_callback()

    def _on_no(self):
        self.go_back()
        if self.on_no_callback:
            self.on_no_callback()
