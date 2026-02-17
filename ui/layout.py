"""Layout manager for split content/button interface."""

import tkinter as tk
from config.settings import settings


class SplitLayout:
    """Layout manager implementing 3/4 content + 1/4 button split."""

    def __init__(self, parent: tk.Widget):
        """Initialize split layout.

        Args:
            parent: Parent widget to contain the layout
        """
        self.parent = parent
        self.content_frame = None
        self.button_frame = None
        self._setup_layout()

    def _setup_layout(self):
        """Set up the split layout with content and button areas."""
        # Main container
        container = tk.Frame(self.parent, bg='black')
        container.pack(fill=tk.BOTH, expand=True)

        # Content area (left 3/4)
        self.content_frame = tk.Frame(
            container,
            width=settings.content_width,
            height=settings.window_height,
            bg='white'
        )
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.content_frame.pack_propagate(False)

        # Button area (right 1/4)
        self.button_frame = tk.Frame(
            container,
            width=settings.button_width,
            height=settings.window_height,
            bg='#2c3e50'
        )
        self.button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.button_frame.pack_propagate(False)

    def get_content_frame(self) -> tk.Frame:
        """Get content area frame.

        Returns:
            Content frame widget
        """
        return self.content_frame

    def get_button_frame(self) -> tk.Frame:
        """Get button area frame.

        Returns:
            Button frame widget
        """
        return self.button_frame

    def clear_content(self):
        """Clear all widgets from content area."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()


class NavigationButtons:
    """Navigation button manager for jog-dial interface."""

    def __init__(self, parent: tk.Frame):
        """Initialize navigation buttons.

        Args:
            parent: Parent frame for buttons (typically button_frame from SplitLayout)
        """
        self.parent = parent
        self.up_button = None
        self.down_button = None
        self.confirm_button = None
        self._setup_buttons()

    def _setup_buttons(self):
        """Create and layout navigation buttons."""
        button_config = {
            'width': 8,
            'height': 2,
            'bg': '#3498db',
            'fg': 'white',
            'font': ('DejaVu Sans', settings.get('font.size_large', 12), 'bold'),
            'relief': tk.RAISED,
            'bd': 3,
            'activebackground': '#2980b9',
            'activeforeground': 'white'
        }

        # Add vertical spacing
        top_spacer = tk.Frame(self.parent, bg='#2c3e50', height=40)
        top_spacer.pack(side=tk.TOP)

        # Up button
        self.up_button = tk.Button(
            self.parent,
            text='▲ UP',
            **button_config
        )
        self.up_button.pack(side=tk.TOP, pady=settings.button_spacing, padx=10)

        # Down button
        self.down_button = tk.Button(
            self.parent,
            text='▼ DOWN',
            **button_config
        )
        self.down_button.pack(side=tk.TOP, pady=settings.button_spacing, padx=10)

        # Confirm button (slightly different styling)
        confirm_config = button_config.copy()
        confirm_config['bg'] = '#27ae60'
        confirm_config['activebackground'] = '#229954'
        confirm_config['height'] = 3

        self.confirm_button = tk.Button(
            self.parent,
            text='✓ OK',
            **confirm_config
        )
        self.confirm_button.pack(side=tk.TOP, pady=settings.button_spacing * 2, padx=10)

    def bind_commands(self, up_cmd, down_cmd, confirm_cmd):
        """Bind commands to navigation buttons.

        Args:
            up_cmd: Command for up button
            down_cmd: Command for down button
            confirm_cmd: Command for confirm button
        """
        self.up_button.config(command=up_cmd)
        self.down_button.config(command=down_cmd)
        self.confirm_button.config(command=confirm_cmd)

    def enable(self):
        """Enable all navigation buttons."""
        self.up_button.config(state=tk.NORMAL)
        self.down_button.config(state=tk.NORMAL)
        self.confirm_button.config(state=tk.NORMAL)

    def disable(self):
        """Disable all navigation buttons."""
        self.up_button.config(state=tk.DISABLED)
        self.down_button.config(state=tk.DISABLED)
        self.confirm_button.config(state=tk.DISABLED)
