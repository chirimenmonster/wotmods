import game

import log
from ModUtils import FileUtils, HotKeysUtils, DecorateUtils

class InputHandler(object):
    _handlers = {}

    def handleKeyEvent(self, event):
        isDown, key, mods, isRepeat = game.convertKeyEvent(event)
        if not isRepeat and isDown:
            for k, handler in self._handlers.iteritems():
                if HotKeysUtils.keysMatch([key], HotKeysUtils.parseHotkeys(k)):
                    try:
                        handler()
                    except Exception:
                        log.current_exception()

    def addEventHandler(self, key, callback):
        self._handlers[key] = callback

im_control = InputHandler()
