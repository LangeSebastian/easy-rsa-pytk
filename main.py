#!/usr/bin/env python3
"""
Easy-RSA PyTk Manager
Main entry point for the application.
"""

import tkinter as tk
import sys
from ui.app import EasyRSAApp


def main():
    """Main entry point."""
    try:
        # Create root window
        root = tk.Tk()

        # Create and run application
        app = EasyRSAApp(root)
        app.run()

    except KeyboardInterrupt:
        print('\nExiting...')
        sys.exit(0)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
