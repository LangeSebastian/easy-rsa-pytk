"""Main application window and controller."""

import tkinter as tk
from config.settings import settings
from ui.layout import SplitLayout, NavigationButtons
from ui.jogdial import JogDialNavigator
from ui.screens.base import BaseScreen


class EasyRSAApp:
    """Main application class."""

    def __init__(self, root: tk.Tk):
        """Initialize application.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.navigator = JogDialNavigator()
        self.layout = None
        self.nav_buttons = None
        self.current_screen: BaseScreen = None

        self._setup_window()
        self._setup_layout()
        self._setup_navigation()

    def _setup_window(self):
        """Set up main window."""
        self.root.title('Easy-RSA Manager')

        # Set window size
        window_width = settings.window_width
        window_height = settings.window_height

        self.root.geometry(f'{window_width}x{window_height}')

        # Fullscreen mode for Raspberry Pi
        if settings.fullscreen:
            self.root.attributes('-fullscreen', True)

        # Prevent resizing
        self.root.resizable(False, False)

        # Black background
        self.root.configure(bg='black')

        # Bind escape key to exit fullscreen (for testing)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))

        # Bind keyboard shortcuts for development/testing
        self.root.bind('<Up>', lambda e: self._on_up())
        self.root.bind('<Down>', lambda e: self._on_down())
        self.root.bind('<Return>', lambda e: self._on_confirm())
        self.root.bind('<BackSpace>', lambda e: self._go_back())

    def _setup_layout(self):
        """Set up split layout."""
        self.layout = SplitLayout(self.root)

    def _setup_navigation(self):
        """Set up navigation buttons."""
        button_frame = self.layout.get_button_frame()
        self.nav_buttons = NavigationButtons(button_frame)
        self.nav_buttons.bind_commands(
            up_cmd=self._on_up,
            down_cmd=self._on_down,
            confirm_cmd=self._on_confirm
        )

    def _on_up(self):
        """Handle up button/key press."""
        if self.current_screen:
            self.current_screen.on_up()

    def _on_down(self):
        """Handle down button/key press."""
        if self.current_screen:
            self.current_screen.on_down()

    def _on_confirm(self):
        """Handle confirm button/key press."""
        if self.current_screen:
            self.current_screen.on_confirm_button()

    def _go_back(self):
        """Handle back navigation."""
        if self.current_screen:
            self.current_screen.go_back()

    def show_screen(self, screen: BaseScreen):
        """Show a screen.

        Args:
            screen: Screen to display
        """
        # Exit current screen
        if self.current_screen:
            self.current_screen.exit()

        # Clear content area
        self.layout.clear_content()

        # Build new screen
        content_frame = self.layout.get_content_frame()
        screen.build(content_frame)

        # Enter new screen
        screen.enter()

        # Update current screen
        self.current_screen = screen

    def run(self):
        """Start the application main loop."""
        # Show main menu
        from ui.screens.main_menu import MainMenuScreen
        self.show_screen(MainMenuScreen(self, self.navigator))

        # Start Tkinter main loop
        self.root.mainloop()

    def quit(self):
        """Quit the application."""
        self.root.quit()
