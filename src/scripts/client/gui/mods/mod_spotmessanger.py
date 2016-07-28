from functools import partial

import game
from PlayerEvents import g_playerEvents
#from gui import g_keyEventHandlers
from gui.Scaleform.daapi.view.battle.shared.indicators import SixthSenseIndicator

from spotmessanger.logger import log
from spotmessanger.events import overrideMethod
from spotmessanger.version import MOD_INFO
from spotmessanger.settings import sm_settings
from spotmessanger.inputhandler import sm_inputKeyManager
from spotmessanger.SpotMessanger import sm_control

confFile = '../res_mods/configs/spotmessanger/spotmessanger.xml'

def init():
    '''Mod's main entry point.  Called by WoT's built-in mod loader.'''

    try:
        log.info(MOD_INFO.NAME + ' ' + MOD_INFO.VERSION_LONG)
        sm_settings.readConfig(confFile)
		
        log.debug('set key event handlers')
        sm_inputKeyManager.addCallback(sm_settings.get('ReloadConfigKey'), partial(sm_settings.readConfig, confFile))
        sm_inputKeyManager.addCallback(sm_settings.get('ActivationHotKey'), sm_control.toggleActive)
        
        g_playerEvents.onAvatarReady += sm_control.onBattleStart
        #g_keyEventHandlers.add(sm_inputKeyManager.handleKeyEvent)
        
    except:
        log.current_exception()

# referring to xvm/src/xpm/xvm_sounds/sixthSense.py 
@overrideMethod(SixthSenseIndicator, "as_showS")
def showSixthSenseIndicator(orig, *args, **kwargs):
    log.debug('activate sixth sense.')
    ret = orig(*args, **kwargs)
    try:
        sm_control.showSixthSenseIndicator()
    except:
        log.current_exception()
    return ret

@overrideMethod(game, "handleKeyEvent")
def handleKeyEvent(orig, *args, **kwargs):
    ret = orig(*args, **kwargs)
    sm_inputKeyManager.handleKeyEvent(*args, **kwargs)
    return ret

