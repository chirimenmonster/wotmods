import Keys

from logger import log

class _InputManager(object):
    _callbacks = {}

    def handleKeyEvent(self, event):
        if event.isKeyDown() and not event.isRepeatedEvent():
            callback = self._callbacks.get(event.key, None)
            if callback:
                try:
                    callback()
                except Exception:
                    log.current_exception()
        return False

    def addCallback(self, keyName, callback):
        try:
            self._callbacks[getattr(Keys, keyName)] = callback
        except AttributeError:
            log.warning('unknown key: "{}"'.format(keyName))


sm_inputKeyManager = _InputManager()
