"""Certificate name input screen using jog-dial character selection."""

import tkinter as tk
from ui.screens.base import BaseScreen
from ui.jogdial import JogDialNavigator
from config.settings import settings


class CertNameInputScreen(BaseScreen):
    """Certificate name input screen with character-by-character selection."""

    def __init__(self, app, navigator: JogDialNavigator, cert_type: str = '', on_submit=None):
        """Initialize cert name input screen.

        Args:
            app: Main application instance
            navigator: Jog-dial navigator instance
            cert_type: Certificate type description
            on_submit: Callback when name is submitted
        """
        super().__init__(app, navigator)
        self.cert_type = cert_type
        self.on_submit_callback = on_submit
        self.current_name = []
        self.char_index = 0

        # Character set for input (alphanumeric + hyphen + underscore)
        self.charset = list('abcdefghijklmnopqrstuvwxyz0123456789-_.')
        self.charset.append('[SPACE]')
        self.charset.append('[DONE]')
        self.charset.append('[DELETE]')
        self.charset.append('[CANCEL]')

    def build(self, content_frame: tk.Frame):
        """Build the input screen UI.

        Args:
            content_frame: Frame to build UI in
        """
        self.content_frame = content_frame

        # Title
        title_bar = tk.Frame(content_frame, bg='#2c3e50', height=40)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        title_label = tk.Label(
            title_bar,
            text=f'Enter {self.cert_type} Certificate Name',
            bg='#2c3e50',
            fg='white',
            font=('DejaVu Sans', settings.get('font.size_normal', 10), 'bold'),
            anchor='w',
            padx=10
        )
        title_label.pack(fill=tk.BOTH, expand=True)

        # Current name display
        self.name_frame = tk.Frame(content_frame, bg='white', height=60)
        self.name_frame.pack(fill=tk.X, pady=10)
        self.name_frame.pack_propagate(False)

        name_label = tk.Label(
            self.name_frame,
            text='Current name:',
            bg='white',
            fg='#7f8c8d',
            font=('DejaVu Sans', settings.get('font.size_small', 8)),
            anchor='w',
            padx=10
        )
        name_label.pack(anchor='w')

        self.name_display = tk.Label(
            self.name_frame,
            text='_',
            bg='white',
            fg='#2c3e50',
            font=('DejaVu Sans Mono', settings.get('font.size_large', 12), 'bold'),
            anchor='w',
            padx=10
        )
        self.name_display.pack(fill=tk.BOTH, expand=True)

        # Character selection area
        char_frame = tk.Frame(content_frame, bg='#ecf0f1', relief=tk.RAISED, bd=2)
        char_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        select_label = tk.Label(
            char_frame,
            text='Select character (↑↓ to change, OK to add):',
            bg='#ecf0f1',
            fg='#2c3e50',
            font=('DejaVu Sans', settings.get('font.size_small', 8)),
            anchor='center',
            pady=5
        )
        select_label.pack()

        self.char_display = tk.Label(
            char_frame,
            text=self.charset[0],
            bg='#3498db',
            fg='white',
            font=('DejaVu Sans Mono', 32, 'bold'),
            anchor='center',
            pady=20
        )
        self.char_display.pack(fill=tk.BOTH, expand=True)

        # Instructions
        info_label = tk.Label(
            content_frame,
            text='Use ↑↓ to select character, OK to add\nSelect [DONE] when finished',
            bg='white',
            fg='#95a5a6',
            font=('DejaVu Sans', settings.get('font.size_small', 8)),
            justify=tk.CENTER,
            pady=5
        )
        info_label.pack()

        # Set up navigator with characters
        self.navigator.set_items(self.charset)
        self._update_display()

    def on_selection_changed(self, index: int, item):
        """Handle character selection change.

        Args:
            index: New selection index
            item: Selected character
        """
        self.char_index = index
        self._update_display()

    def on_confirm(self, index: int, item):
        """Handle character confirmation.

        Args:
            index: Confirmed item index
            item: Selected character
        """
        char = self.charset[index]

        if char == '[DONE]':
            self._submit_name()
        elif char == '[DELETE]':
            if self.current_name:
                self.current_name.pop()
                self._update_display()
        elif char == '[CANCEL]':
            self.go_back()
        elif char == '[SPACE]':
            self.current_name.append(' ')
            self._update_display()
        else:
            self.current_name.append(char)
            self._update_display()

    def _update_display(self):
        """Update the display."""
        # Update name display
        current_text = ''.join(self.current_name)
        if not current_text:
            current_text = '_'
        self.name_display.config(text=current_text)

        # Update character display
        char = self.charset[self.char_index]
        display_char = char
        if char == '[SPACE]':
            display_char = '␣'
        elif char.startswith('['):
            display_char = char[1:-1]

        self.char_display.config(text=display_char)

    def _submit_name(self):
        """Submit the entered name."""
        name = ''.join(self.current_name).strip()

        if not name:
            from ui.widgets import MessageBox
            MessageBox(self.content_frame, 'Error', 'Name cannot be empty', ['OK']).get_result()
            return

        # Go back to previous screen
        self.go_back()

        # Call callback
        if self.on_submit_callback:
            self.on_submit_callback(name)
