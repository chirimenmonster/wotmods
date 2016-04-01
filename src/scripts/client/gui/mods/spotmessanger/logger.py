
import inspect
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from version import MOD_INFO

class Logger(object):
    _enableDebug = False

    def setDebug(self, bool):
        self._enableDebug = bool

    def _addLineNo(self, msg):
        frame = inspect.currentframe(2)
        return '({}, {}): {}'.format(frame.f_code.co_filename, frame.f_lineno, msg)

    def error(self, msg, *args, **kwargs):
        BigWorld.logError(MOD_INFO.NAME, self._addLineNo(msg), None)

    def warning(self, msg, *args, **kwargs):
        BigWorld.logWarning(MOD_INFO.NAME, self._addLineNo(msg), None)

    def note(self, msg, *args, **kwargs):
        BigWorld.logNotice(MOD_INFO.NAME, msg, None)

    def info(self, msg, *args, **kwargs):
        BigWorld.logInfo(MOD_INFO.NAME, msg, None)

    def debug(self, msg, *args, **kwargs):
        if self._enableDebug:
            BigWorld.logDebug(MOD_INFO.NAME, self._addLineNo(msg), None)

    def current_exception(self):
        LOG_CURRENT_EXCEPTION()

log = Logger()
