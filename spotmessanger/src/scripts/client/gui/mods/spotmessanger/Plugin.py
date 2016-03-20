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


    @classmethod
    def readConfig(cls):
        log.debug("searching config file: %s" % cls.confFile)
        cfg = ResMgr.openSection(cls.confFile)
        if cfg:
            log.info("config found: %s" % cls.confFile)
            value = FileUtils.readElement(cfg, getattr(cls, 'myConf'), 'SpotMessanger', 'root')
            setattr(cls, 'myConf', value)
        else:
            log.warning("no config found: %s" % cls.confFile)

    @classmethod
    def reloadConfig(cls):
        cls.readConfig()
