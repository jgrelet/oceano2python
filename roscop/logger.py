"""Module for setting up logging."""

import logging
import sys

from version import NAME

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

LOG_FORMATS = {
    'DEBUG': '%(levelname)-5s [%(filename)s:%(lineno)d]  %(message)s',
    'INFO': '%(levelname)-5s: %(message)s',
    'WARNING': '%(levelname)-5s: %(message)s',
    'ERROR': '%(levelname)-5s [%(filename)s:%(lineno)d]  %(message)s',
    'CRITICAL': '%(levelname)-5s [%(filename)s:%(lineno)d]  %(message)s',
    'LOG': '%(levelname)-5s %(asctime)s [%(filename)s:%(lineno)d]  %(message)s',
}


def configure_logger(stream_level='INFO', debug_file=None):
    """Configure logging with the given level.

    Args:
        stream_level (str, optional): set up logging level. Defaults to 'INFO'.
        debug_file (str, optional): write logging to file. Defaults to None.
 
    Returns:
        logger: a reference to a logger instance
    """
    # Set up 'mooringSimulator' logger
    logger = logging.getLogger(NAME)
    logger.setLevel(LOG_LEVELS[stream_level])

    # Remove all attached handlers, in case there was
    # a logger with using the name 'mooringSimulator'
    del logger.handlers[:]

    # Create a file handler if a log file is provided
    if debug_file is not None:
        debug_formatter = logging.Formatter(
            LOG_FORMATS['LOG'], datefmt='%m/%d/%Y %H:%M:%S')
        file_handler = logging.FileHandler(debug_file)
        file_handler.setLevel(LOG_LEVELS['DEBUG'])
        file_handler.setFormatter(debug_formatter)
        logger.addHandler(file_handler)

    # Get settings based on the given stream_level
    log_formatter = logging.Formatter(LOG_FORMATS[stream_level])
    log_level = LOG_LEVELS[stream_level]

    # Create a stream handler
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    return logger
