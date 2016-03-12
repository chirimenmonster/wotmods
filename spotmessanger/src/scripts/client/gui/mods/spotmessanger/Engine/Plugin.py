import game
import ResMgr
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_NOTE
from ModUtils import FileUtils, HotKeysUtils, DecorateUtils
old_handleKeyEvent = None

class Plugin(object):
    handlers = {}
    pluginEnable = True
    debug = False
    pluginName = 'Plugin'
    confFile = ''

    @classmethod
    def new_handleKeyEvent(cls, event):
        global old_handleKeyEvent
        try:
            isDown, key, mods, isRepeat = game.convertKeyEvent(event)
            if not isRepeat and isDown:
                for k, v in cls.handlers.iteritems():
                    n = HotKeysUtils.parseHotkeys(k)
                    if HotKeysUtils.keysMatch([key], n):
                        v()
                        break

        except Exception as e:
            LOG_CURRENT_EXCEPTION()
        finally:
            return old_handleKeyEvent(event)

    @classmethod
    def addEventHandler(cls, key, callback):
        Plugin.handlers[key] = callback

    @classmethod
    def init(cls):
        cls.pluginEnable = True
        cls.pluginName = cls.__name__
        cls.debug = False

    @classmethod
    def run(cls):
        global old_handleKeyEvent
        if old_handleKeyEvent is None:
            old_handleKeyEvent = game.handleKeyEvent
            game.handleKeyEvent = Plugin.new_handleKeyEvent
        return

    @classmethod
    def myGetAttr(cls, name):
        return getattr(cls, name)

    @classmethod
    def mySetAttr(cls, name, value):
        setattr(cls, name, value)

    @classmethod
    def readConfig(cls):
        print "[SpotMessanger] read config: %s" % cls.confFile
        cfg = ResMgr.openSection(cls.confFile)
        if cfg:
            value = FileUtils.readElement(cfg, cls.myGetAttr('myConf'), 'SpotMessanger', 'root')
        else:
            LOG_WARNING("%s: no config found" % path)
            value = defset
        cls.mySetAttr('myConf', value)
        if value.has_key('pluginEnable'):
            cls.pluginEnable = value['pluginEnable']
        else:
            cls.pluginEnable = True
        if value.has_key('debug'):
            cls.debug = value['debug']
        else:
            cls.debug = False
        if cls.debug:
            print value

    @classmethod
    def reloadConfig(cls):
        cls.readConfig()
