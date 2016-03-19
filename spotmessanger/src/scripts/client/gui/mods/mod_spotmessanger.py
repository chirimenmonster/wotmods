import game
from gui.Scaleform.Battle import Battle
from spotmessanger import log
from spotmessanger.events import overrideMethod
from spotmessanger.const import MOD_INFO
from spotmessanger.SpotMessanger import SpotMessanger
from spotmessanger.Plugin import Plugin

def init():
    '''Mod's main entry point.  Called by WoT's built-in mod loader.'''

    try:
        log.info(MOD_INFO.NAME + ' ' + MOD_INFO.VERSION_LONG)

        SpotMessanger.readConfig()
        if SpotMessanger.pluginEnable:
            log.info(MOD_INFO.NAME + ' mod enable')
            SpotMessanger.run()
			
    except:
        log.current_exception()

@overrideMethod(Battle, "_showSixthSenseIndicator")
def showSixthSenseIndicator(orig, *args, **kwargs):
    log.debug('activate sixth sense!')
    ret = orig(*args, **kwargs)
    SpotMessanger.showSixthSenseIndicator(*args, **kwargs)
    return ret

@overrideMethod(game, "handleKeyEvent")
def handleKeyEvent(orig, *args, **kwargs):
    ret = orig(*args, **kwargs)
    Plugin.handleKeyEvent(*args, **kwargs)
    return ret

