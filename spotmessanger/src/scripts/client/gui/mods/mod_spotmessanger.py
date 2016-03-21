import game
from gui.Scaleform.Battle import Battle
from spotmessanger import log
from spotmessanger.events import overrideMethod
from spotmessanger.const import MOD_INFO
from spotmessanger.SpotMessanger import SpotMessanger
from spotmessanger.Plugin import Plugin
from spotmessanger.settings import Settings

confFile = '../res_mods/configs/spotmessanger/settings.xml'

def readConfig():
    SpotMessanger.settings = Settings.readConfig(confFile)
    print SpotMessanger.settings
    SpotMessanger.isActive = SpotMessanger.settings['ActiveByDefault']

def init():
    '''Mod's main entry point.  Called by WoT's built-in mod loader.'''

    try:
        log.info(MOD_INFO.NAME + ' ' + MOD_INFO.VERSION_LONG)
        readConfig()
		
        log.info('set key event handlers')
        Plugin.addEventHandler(SpotMessanger.settings['ReloadConfigKey'], readConfig)
        Plugin.addEventHandler(SpotMessanger.settings['ActivationHotKey'], SpotMessanger.handleActivationHotkey)
			
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

