import os
import sys
import logging

def init_log(logger, filename=None, loglevel=None):
    """
    Initializes the log file in the proper format.
    
    Arguments:
    
        filename (str): Path to a file. Or None if logging is to
                         be disabled.
        loglevel (str): Determines the level of the log output.
    """
    
    formatter = logging.Formatter(
                    '[%(asctime)s] %(levelname)s: %(name)s: %(message)s'
                )
    
    if loglevel:
        logger.setLevel(getattr(logging, loglevel))
    
    # We will allways print warnings and higher to stderr
    ch = logging.StreamHandler()
    ch.setLevel('WARNING')
    ch.setFormatter(formatter)
    
    if filename:
        fi = logging.FileHandler(filename, encoding='utf-8')
        if loglevel:
            fi.setLevel(getattr(logging, loglevel))
        fi.setFormatter(formatter)
        logger.addHandler(fi)
    # If no logfile is provided we print all log messages that the user has 
    # defined to stderr
    else:
        if loglevel:
            ch.setLevel(getattr(logging, loglevel))
    
    logger.addHandler(ch)
        

def get_log_stream(logger):
    """
    Returns a stream to the root log file.
    If there is no logfile return the stderr log stream
    
    Returns:
        A stream to the root log file or stderr stream.
    """
    
    file_stream = None
    log_stream = None
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            file_stream = handler.stream
        else:
            log_stream = handler.stream
    
    if file_stream:
        return file_stream
    
    return log_stream