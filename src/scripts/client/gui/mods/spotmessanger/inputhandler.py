import Keys
from logger import log

_callbacks = {}


def handleKeyEvent(event):
    if event.isKeyDown() and not event.isRepeatedEvent():
        callback = _callbacks.get(event.key, None)
        if callback:
            try:
                callback()
            except Exception:
                log.current_exception()
    return False

def addKeyEventCallback(keyName, callback):
    try:
        _callbacks[getattr(Keys, keyName)] = callback
    except AttributeError:
        log.warning('unknown key: "{}"'.format(keyName))
