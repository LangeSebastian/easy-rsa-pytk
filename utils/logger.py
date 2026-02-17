"""Logging utilities for Easy-RSA PyTk."""

import logging
import os
from pathlib import Path
from datetime import datetime
from config.settings import settings


def setup_logger(name: str = 'easy-rsa-pytk') -> logging.Logger:
    """Set up application logger.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if logger.handlers:
        return logger

    # Set level from settings
    log_level = getattr(logging, settings.get('log_level', 'INFO'))
    logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler
    log_file = settings.get('log_file')

    if log_file:
        try:
            # Create log directory if needed
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)

            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)

        except (PermissionError, OSError) as e:
            logger.warning(f'Could not create file log handler: {e}')

    return logger


# Global logger instance
logger = setup_logger()


def log_operation(operation: str, details: str = '', level: str = 'INFO'):
    """Log an operation.

    Args:
        operation: Operation name
        details: Operation details
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    """
    log_func = getattr(logger, level.lower(), logger.info)
    message = f'{operation}'

    if details:
        message += f': {details}'

    log_func(message)


def log_error(error: Exception, context: str = ''):
    """Log an error with context.

    Args:
        error: Exception object
        context: Error context
    """
    message = f'Error in {context}: {type(error).__name__}: {str(error)}'
    logger.error(message, exc_info=True)


def log_command(command: str, result: bool, output: str = ''):
    """Log command execution.

    Args:
        command: Command executed
        result: Success/failure
        output: Command output
    """
    status = 'SUCCESS' if result else 'FAILED'
    logger.info(f'Command {status}: {command}')

    if output and not result:
        logger.debug(f'Command output: {output}')


class OperationLogger:
    """Context manager for logging operations."""

    def __init__(self, operation: str):
        """Initialize operation logger.

        Args:
            operation: Operation name
        """
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        """Enter context."""
        self.start_time = datetime.now()
        logger.info(f'Starting operation: {self.operation}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        duration = (datetime.now() - self.start_time).total_seconds()

        if exc_type is None:
            logger.info(f'Completed operation: {self.operation} ({duration:.2f}s)')
        else:
            logger.error(f'Failed operation: {self.operation} ({duration:.2f}s): {exc_val}')

        return False  # Don't suppress exceptions
