#!/usr/bin/env python3
"""
Easy-RSA PyTk Manager
Main entry point for the application.
"""

import tkinter as tk
import sys
from utils.logger import logger
from ui.app import EasyRSAApp


def _setup_exception_logging():
    """Redirect all uncaught exceptions to the log file."""
    def excepthook(exc_type, exc_value, exc_tb):
        if exc_type is KeyboardInterrupt:
            sys.exit(0)
        logger.critical('Uncaught exception', exc_info=(exc_type, exc_value, exc_tb))

    sys.excepthook = excepthook


def main():
    """Main entry point."""
    _setup_exception_logging()

    try:
        # Create root window
        root = tk.Tk()

        # Redirect Tkinter callback exceptions to the log file
        def tk_exception_handler(exc_type, exc_value, exc_tb):
            logger.error('Tkinter callback exception', exc_info=(exc_type, exc_value, exc_tb))

        root.report_callback_exception = tk_exception_handler

        # Create and run application
        app = EasyRSAApp(root)
        app.run()

    except KeyboardInterrupt:
        logger.info('Exiting (KeyboardInterrupt)')
        sys.exit(0)
    except Exception as e:
        logger.critical(f'Fatal error: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
