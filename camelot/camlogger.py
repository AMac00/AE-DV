'''
Created on 17-Feb-2014

@author: smaturi
'''
import logging
import sys


__logger_name = 'camelot'
__camelot_handlers = []


class LoggerWrapper(object):
    # Lightweight wrapper class to add extra information onto log messages
    # logger calls.
    # '''
    levelnames = ('debug', 'info', 'warning', 'error', 'critical', 'exception')

    def __init__(self, name):
        # '''
        # :parameter name: the name for the logger instance (typically what you
        #    would pass to ``logging.getLogger()``)
        # '''
        self._logger = logging.getLogger('camelot')
        self._logger_name = name

    def __getattr__(self, name):
        attr = getattr(self._logger, name)
        if name in self.levelnames:
            def log_with_prefix(message, *args, **kwargs):
                message = '[{}] - {}'.format(self._logger_name, message)
                attr(message, *args, **kwargs)
            return log_with_prefix
        else:
            return attr
        return attr


def getLogger(name):
    '''Creates logger in the Camelot module

    :parameter name: name for the logger
    '''
    if not name.startswith(__logger_name + '.') and not name == __logger_name:
        name = __logger_name + '.' + name
    return logging.getLogger(name)


def setLevel(level):
    '''Set's logger level for Camelot logging

    :parameter value: logging level
    '''
    root_logger = logging.getLogger(__logger_name)
    root_logger.setLevel(level)
    for handler in root_logger.handlers:
        handler.setLevel(level)


def enable_logging():
    '''Enables Camelot module style logging.
    '''
    root_logger = logging.getLogger(__logger_name)
    if __camelot_handlers:
        return
    stdout_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
    root_logger.addHandler(stdout_handler)
    root_logger.setLevel(logging.DEBUG)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)
    __camelot_handlers.append(stdout_handler)


def disable_logging():
    '''Disables Camelot module style logging.
    '''
    root_logger = logging.getLogger(__logger_name)
    count_handlers = __camelot_handlers
    for hadl in __camelot_handlers:
        root_logger.removeHandler(hadl)
    del __camelot_handlers[:]
