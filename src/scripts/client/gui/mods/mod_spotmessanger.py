import game
from PlayerEvents import g_playerEvents
from gui.Scaleform.Battle import Battle
from spotmessanger.logger import log
from spotmessanger.events import overrideMethod
from spotmessanger.version import MOD_INFO
from spotmessanger.settings import st_control
from spotmessanger.inputhandler import im_control
from spotmessanger.SpotMessanger import sm_control

confFile = '../res_mods/configs/spotmessanger/spotmessanger.xml'

def init():
    '''Mod's main entry point.  Called by WoT's built-in mod loader.'''

    try:
        log.info(MOD_INFO.NAME + ' ' + MOD_INFO.VERSION_LONG)
        settings = _readConfig(confFile)
		
        log.debug('set key event handlers')
        im_control.addEventHandler(settings['ReloadConfigKey'], _readConfig)
        im_control.addEventHandler(settings['ActivationHotKey'], _toggleActive)
        
        g_playerEvents.onAvatarReady += _on_avatar_ready
        
    except:
        log.current_exception()


def _readConfig(file):
    settings = st_control.readConfig(file)
    log.debug('settings = {}'.format(str(settings)))
    sm_control.setConfig(settings)
    return settings

def _on_avatar_ready():
    log.debug('onAvatarReady: initialize SpotMessanger')
    sm_control.initialize()

def _toggleActive():
    sm_control.toggleActive()

@overrideMethod(Battle, "_showSixthSenseIndicator")
def showSixthSenseIndicator(orig, *args, **kwargs):
    log.debug('activate sixth sense.')
    ret = orig(*args, **kwargs)
    sm_control.showSixthSenseIndicator()
    return ret

@overrideMethod(game, "handleKeyEvent")
def handleKeyEvent(orig, *args, **kwargs):
    ret = orig(*args, **kwargs)
    im_control.handleKeyEvent(*args, **kwargs)
    return ret

