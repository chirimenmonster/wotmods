import game
import ResMgr

import log
from ModUtils import FileUtils, HotKeysUtils, DecorateUtils

class Plugin(object):
    handlers = {}
    pluginEnable = True
    debug = False
    pluginName = 'Plugin'
    confFile = ''

    @classmethod
    def handleKeyEvent(cls, event):
        isDown, key, mods, isRepeat = game.convertKeyEvent(event)
        if not isRepeat and isDown:
            for k, handler in cls.handlers.iteritems():
                if HotKeysUtils.keysMatch([key], HotKeysUtils.parseHotkeys(k)):
                    try:
                        handler()
                    except Exception:
                        log.current_exception()

    @classmethod
    def addEventHandler(cls, key, callback):
        Plugin.handlers[key] = callback
