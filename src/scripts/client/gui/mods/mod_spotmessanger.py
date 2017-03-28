from functools import partial

import game
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.battle.shared.indicators import SixthSenseIndicator

from spotmessanger.logger import log
from spotmessanger.events import overrideMethod
from spotmessanger.version import MOD_INFO
from spotmessanger.settings import Settings
from spotmessanger.control import SpotMessanger
from spotmessanger.inputhandler import handleKeyEvent, addKeyEventCallback

conf_base = [ '../res_mods', '../mods', '' ]
conf_file = 'configs/spotmessanger/spotmessanger.xml'

_control = None

def init():
    '''Mod's main entry point.  Called by WoT's built-in mod loader.'''
    global _control

    try:
        log.info(MOD_INFO.NAME + ' ' + MOD_INFO.VERSION_LONG)
        settings = Settings(conf_file, conf_base)
        _control = SpotMessanger(settings)
        
        log.debug('set key event handlers')
        addKeyEventCallback(settings['ReloadConfigKey'], partial(_control.reloadConfig, conf_file, conf_base))
        addKeyEventCallback(settings['ActivationHotKey'], _control.toggleActive)
        
        g_playerEvents.onAvatarReady += _control.onBattleStart

    except:
        log.current_exception()

# referring to xvm/src/xpm/xvm_sounds/sixthSense.py 
@overrideMethod(SixthSenseIndicator, "as_showS")
def _showSixthSenseIndicator(orig, *args, **kwargs):
    log.debug('activate sixth sense.')
    ret = orig(*args, **kwargs)
    try:
        _control.showSixthSenseIndicator()
    except:
        log.current_exception()
    return ret

@overrideMethod(game, "handleKeyEvent")
def _handleKeyEvent(orig, *args, **kwargs):
    ret = orig(*args, **kwargs)
    handleKeyEvent(*args, **kwargs)
    return ret
