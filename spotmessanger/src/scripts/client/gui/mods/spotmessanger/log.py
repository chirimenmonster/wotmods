
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from const import MOD_INFO

flgDebugMsg = False

def error(msg, *args, **kwargs):
    BigWorld.logError(MOD_INFO.NAME, msg, None)

def warning(msg, *args, **kwargs):
    BigWorld.logWarning(MOD_INFO.NAME, msg, None)

def note(msg, *args, **kwargs):
    BigWorld.logNotice(MOD_INFO.NAME, msg, None)

def info(msg, *args, **kwargs):
    BigWorld.logInfo(MOD_INFO.NAME, msg, None)

def debug(msg, *args, **kwargs):
    if flgDebugMsg:
        BigWorld.logDebug(MOD_INFO.NAME, msg, None)

def current_exception():
    LOG_CURRENT_EXCEPTION()
