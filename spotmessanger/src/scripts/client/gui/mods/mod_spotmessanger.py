import game
from PlayerEvents import g_playerEvents
from gui.Scaleform.Battle import Battle
from spotmessanger import log
from spotmessanger.events import overrideMethod
from spotmessanger.const import MOD_INFO
from spotmessanger.Plugin import Plugin
from spotmessanger.settings import Settings
from spotmessanger.SpotMessanger import sm_control

confFile = '../res_mods/configs/spotmessanger/spotmessanger.xml'

def init():
    '''Mod's main entry point.  Called by WoT's built-in mod loader.'''

    try:
        log.info(MOD_INFO.NAME + ' ' + MOD_INFO.VERSION_LONG)
        log.flgDebugMsg = True
        settings = _readConfig()
		
        log.info('set key event handlers')
        Plugin.addEventHandler(settings['ReloadConfigKey'], _readConfig)
        Plugin.addEventHandler(settings['ActivationHotKey'], _toggleActive)
        
        g_playerEvents.onAvatarReady += _on_avatar_ready
        
    except:
        log.current_exception()


def _readConfig():
    settings = Settings.readConfig(confFile)
    log.flgDebugMsg = settings['Debug']
    log.debug('settings = {}'.format(str(settings)))
    sm_control.settings = settings
    return settings

def _on_avatar_ready():
    log.debug('onAvatarReady: initialize SpotMessanger')
    sm_control.initialize()

def _toggleActive():
    sm_control.toggleActive()

@overrideMethod(Battle, "_showSixthSenseIndicator")
def showSixthSenseIndicator(orig, *args, **kwargs):
    log.info('activate sixth sense.')
    ret = orig(*args, **kwargs)
    sm_control.showSixthSenseIndicator()
    return ret

@overrideMethod(game, "handleKeyEvent")
def handleKeyEvent(orig, *args, **kwargs):
    ret = orig(*args, **kwargs)
    Plugin.handleKeyEvent(*args, **kwargs)
    return ret

