'''
Created on 08-Oct-2015

@author: smaturi
'''
import time
from collections import OrderedDict
import sys
try:
    from threading import _get_ident as get_ind
except ImportError:
    from threading import get_ident as get_ind


class TimeoutException(Exception):
    pass


def wait_until(func, expected_output=True, timeout=30, period=1, params=[]):
    mustend = time.time() + timeout
    while time.time() < mustend:
        if func(*params) == expected_output:
            return
        time.sleep(period)
    raise TimeoutException('Timedout after: %s for execution: %s' % (
        timeout, func))


class CamelotOrderedDict(OrderedDict):
    '''Overriding OrderedDict to get our own order displayed.
    '''
    def __repr__(self, _repr_running={}):
        call_key = id(self), get_ind()
        if call_key in _repr_running:
            return '...'
        _repr_running[call_key] = 1
        try:
            if not self:
                return '{}'
            final_str = '{\n'
            for item in self.items():
                key = item[0]
                value = item[1]
                if sys.version_info < (3, 0):
                    if isinstance(item[1], str) or isinstance(
                            item[1], unicode):
                        value = "'%s'" % item[1]
                else:
                    if isinstance(item[1], str):
                        value = "'%s'" % item[1]
                final_str = "%s '%s': %s,\n" % (final_str, key, value)
            final_str = '%s}' % final_str
            return final_str
        finally:
            del _repr_running[call_key]
