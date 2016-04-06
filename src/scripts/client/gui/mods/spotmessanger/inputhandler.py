import Keys

from logger import log

class InputHandler(object):
    _handlers = {}

    def handleKeyEvent(self, event):
        if event.isKeyDown() and not event.isRepeatedEvent():
            handler = self._handlers.get(event.key, None)
            if handler:
                try:
                    handler()
                except Exception:
                    log.current_exception()

    def addEventHandler(self, keyName, callback):
        key = getattr(Keys, keyName, None)
        if not key:
            log.warning('unknown key: "{}"'.format(keyName))
            return
        self._handlers[key] = callback


im_control = InputHandler()

