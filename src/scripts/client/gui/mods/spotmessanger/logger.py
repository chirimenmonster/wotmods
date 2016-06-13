
import inspect
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from version import MOD_INFO

class LOGLEVEL:
    class LABELS:
        ERR     = 'error'
        WARN    = 'warning'
        NOTE    = 'notice'
        INFO    = 'info'
        DEBUG   = 'debug'
    ERR     = 3
    WARN    = 4
    NOTE    = 5
    INFO    = 6
    DEBUG   = 7
    VALUES = {
        LABELS.ERR:     ERR,
        LABELS.WARN:    WARN,
        LABELS.NOTE:    NOTE,
        LABELS.INFO:    INFO,
        LABELS.DEBUG:   DEBUG
    }
    LIST = [
        LABELS.ERR,
        LABELS.WARN,
        LABELS.NOTE,
        LABELS.INFO,
        LABELS.DEBUG
    ]
    REV = { v: k for k, v in VALUES.items() }

class Logger(object):
    _enableDebug = False
    _logLevel = LOGLEVEL.INFO

    def setDebug(self, bool):
        self._enableDebug = bool

    def setLogLevel(self, label):
        if self._enableDebug:
            self._logLevel = LOGLEVEL.DEBUG
        else:
            if label in LOGLEVEL.VALUES:
                self._logLevel = LOGLEVEL.VALUES[label]
        log.debug('set log level: {}'.format(LOGLEVEL.REV[self._logLevel]))

    def _addLineNo(self, msg):
        frame = inspect.currentframe(2)
        return '({}, {}): {}'.format(frame.f_code.co_filename, frame.f_lineno, msg)

    def error(self, msg, *args, **kwargs):
        if self._logLevel >= LOGLEVEL.ERR:
            BigWorld.logError(MOD_INFO.NAME, self._addLineNo(msg), None)

    def warning(self, msg, *args, **kwargs):
        if self._logLevel >= LOGLEVEL.WARN:
            BigWorld.logWarning(MOD_INFO.NAME, self._addLineNo(msg), None)

    def note(self, msg, *args, **kwargs):
        if self._logLevel >= LOGLEVEL.NOTE:
            BigWorld.logNotice(MOD_INFO.NAME, msg, None)

    def info(self, msg, *args, **kwargs):
        if self._logLevel >= LOGLEVEL.INFO:
            BigWorld.logInfo(MOD_INFO.NAME, msg, None)

    def debug(self, msg, *args, **kwargs):
        if self._logLevel >= LOGLEVEL.DEBUG:
            BigWorld.logDebug(MOD_INFO.NAME, self._addLineNo(msg), None)

    def current_exception(self):
        LOG_CURRENT_EXCEPTION()

log = Logger()
