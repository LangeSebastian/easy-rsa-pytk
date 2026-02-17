"""Custom widgets optimized for small display and jog-dial navigation."""

import tkinter as tk
from tkinter import font
from typing import List, Callable, Optional, Any
from config.settings import settings


class MenuList(tk.Frame):
    """Scrollable list widget with highlight for jog-dial navigation."""

    def __init__(self, parent, visible_items: int = 6, item_height: int = 40):
        """Initialize menu list.

        Args:
            parent: Parent widget
            visible_items: Number of items visible at once
            item_height: Height of each item in pixels
        """
        super().__init__(parent, bg='white')
        self.visible_items = visible_items
        self.item_height = item_height
        self.items: List[str] = []
        self.current_index = 0
        self.scroll_offset = 0
        self.item_labels: List[tk.Label] = []

        self._setup_ui()

    def _setup_ui(self):
        """Set up list UI."""
        # Create container for list items
        self.list_container = tk.Frame(self, bg='white')
        self.list_container.pack(fill=tk.BOTH, expand=True)

        # Create label widgets for visible items
        for i in range(self.visible_items):
            label = tk.Label(
                self.list_container,
                text='',
                bg='white',
                fg='black',
                font=('DejaVu Sans', settings.get('font.size_normal', 10)),
                anchor='w',
                padx=10,
                height=2,
                relief=tk.FLAT
            )
            label.pack(fill=tk.X)
            self.item_labels.append(label)

    def set_items(self, items: List[str]):
        """Set list items.

        Args:
            items: List of item strings to display
        """
        self.items = items
        self.current_index = 0
        self.scroll_offset = 0
        self._update_display()

    def set_selection(self, index: int):
        """Set selected item index.

        Args:
            index: Index to select
        """
        if 0 <= index < len(self.items):
            self.current_index = index
            self._adjust_scroll()
            self._update_display()

    def _adjust_scroll(self):
        """Adjust scroll offset based on current selection."""
        if self.current_index < self.scroll_offset:
            self.scroll_offset = self.current_index
        elif self.current_index >= self.scroll_offset + self.visible_items:
            self.scroll_offset = self.current_index - self.visible_items + 1

    def _update_display(self):
        """Update the display of visible items."""
        for i, label in enumerate(self.item_labels):
            item_index = self.scroll_offset + i

            if item_index < len(self.items):
                label.config(text=self.items[item_index])

                # Highlight current item
                if item_index == self.current_index:
                    label.config(bg='#3498db', fg='white', font=('DejaVu Sans', settings.get('font.size_normal', 10), 'bold'))
                else:
                    label.config(bg='white', fg='black', font=('DejaVu Sans', settings.get('font.size_normal', 10)))
            else:
                label.config(text='', bg='white')

    def clear(self):
        """Clear all items."""
        self.items = []
        self.current_index = 0
        self.scroll_offset = 0
        self._update_display()


class InfoPanel(tk.Frame):
    """Panel for displaying read-only information."""

    def __init__(self, parent, title: str = ''):
        """Initialize info panel.

        Args:
            parent: Parent widget
            title: Panel title
        """
        super().__init__(parent, bg='white', relief=tk.RAISED, bd=1)
        self.title = title
        self._setup_ui()

    def _setup_ui(self):
        """Set up panel UI."""
        if self.title:
            title_label = tk.Label(
                self,
                text=self.title,
                bg='#34495e',
                fg='white',
                font=('DejaVu Sans', settings.get('font.size_large', 12), 'bold'),
                anchor='w',
                padx=10,
                pady=5
            )
            title_label.pack(fill=tk.X)

        # Content area with scrollbar
        content_frame = tk.Frame(self, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(content_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget = tk.Text(
            content_frame,
            wrap=tk.WORD,
            bg='white',
            fg='black',
            font=('DejaVu Sans Mono', settings.get('font.size_small', 8)),
            yscrollcommand=scrollbar.set,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_widget.yview)

        self.text_widget.config(state=tk.DISABLED)

    def set_text(self, text: str):
        """Set panel text content.

        Args:
            text: Text to display
        """
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, text)
        self.text_widget.config(state=tk.DISABLED)

    def append_text(self, text: str):
        """Append text to panel.

        Args:
            text: Text to append
        """
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, text)
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.see(tk.END)

    def clear(self):
        """Clear panel text."""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)


class ProgressIndicator(tk.Frame):
    """Progress indicator for long-running operations."""

    def __init__(self, parent):
        """Initialize progress indicator.

        Args:
            parent: Parent widget
        """
        super().__init__(parent, bg='white')
        self._setup_ui()

    def _setup_ui(self):
        """Set up progress indicator UI."""
        self.label = tk.Label(
            self,
            text='',
            bg='white',
            fg='#2c3e50',
            font=('DejaVu Sans', settings.get('font.size_normal', 10)),
            anchor='center'
        )
        self.label.pack(pady=10)

        self.progress_bar = tk.Canvas(
            self,
            height=20,
            bg='white',
            highlightthickness=0
        )
        self.progress_bar.pack(fill=tk.X, padx=20, pady=5)

        self.status_label = tk.Label(
            self,
            text='',
            bg='white',
            fg='#7f8c8d',
            font=('DejaVu Sans', settings.get('font.size_small', 8)),
            anchor='center'
        )
        self.status_label.pack(pady=5)

    def set_message(self, message: str):
        """Set progress message.

        Args:
            message: Message to display
        """
        self.label.config(text=message)

    def set_progress(self, percent: float):
        """Set progress percentage.

        Args:
            percent: Progress percentage (0-100)
        """
        self.progress_bar.delete('all')
        width = self.progress_bar.winfo_width()
        if width <= 1:
            width = 320

        # Draw background
        self.progress_bar.create_rectangle(
            0, 0, width, 20,
            fill='#ecf0f1',
            outline='#bdc3c7'
        )

        # Draw progress
        progress_width = int(width * (percent / 100))
        self.progress_bar.create_rectangle(
            0, 0, progress_width, 20,
            fill='#3498db',
            outline=''
        )

    def set_status(self, status: str):
        """Set status text.

        Args:
            status: Status text
        """
        self.status_label.config(text=status)

    def start_indeterminate(self):
        """Start indeterminate progress animation."""
        self.set_message('Working...')
        self._animate_indeterminate()

    def _animate_indeterminate(self):
        """Animate indeterminate progress."""
        # Simple animation placeholder
        self.set_progress(50)

    def stop(self):
        """Stop progress indicator."""
        self.set_progress(100)
        self.set_status('Complete')


class MessageBox(tk.Toplevel):
    """Modal message box for confirmations and alerts."""

    def __init__(self, parent, title: str, message: str, buttons: List[str] = None):
        """Initialize message box.

        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display
            buttons: List of button labels (default: ['OK'])
        """
        super().__init__(parent)
        self.result = None
        self.buttons_list = buttons or ['OK']

        self.title(title)
        self.geometry('400x200')
        self.resizable(False, False)
        self.configure(bg='white')

        # Center on parent
        self.transient(parent)
        self.grab_set()

        self._setup_ui(title, message)

    def _setup_ui(self, title: str, message: str):
        """Set up message box UI.

        Args:
            title: Dialog title
            message: Message text
        """
        # Title
        title_label = tk.Label(
            self,
            text=title,
            bg='#34495e',
            fg='white',
            font=('DejaVu Sans', settings.get('font.size_large', 12), 'bold'),
            pady=10
        )
        title_label.pack(fill=tk.X)

        # Message
        message_label = tk.Label(
            self,
            text=message,
            bg='white',
            fg='#2c3e50',
            font=('DejaVu Sans', settings.get('font.size_normal', 10)),
            wraplength=350,
            justify=tk.CENTER,
            pady=20
        )
        message_label.pack(fill=tk.BOTH, expand=True)

        # Buttons
        button_frame = tk.Frame(self, bg='white')
        button_frame.pack(pady=10)

        for btn_text in self.buttons_list:
            btn = tk.Button(
                button_frame,
                text=btn_text,
                command=lambda t=btn_text: self._on_button(t),
                bg='#3498db',
                fg='white',
                font=('DejaVu Sans', settings.get('font.size_normal', 10)),
                padx=20,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=5)

    def _on_button(self, button_text: str):
        """Handle button click.

        Args:
            button_text: Text of clicked button
        """
        self.result = button_text
        self.destroy()

    def get_result(self) -> Optional[str]:
        """Get dialog result.

        Returns:
            Selected button text or None
        """
        self.wait_window()
        return self.result
