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

conf_base = [ '../mods' ]
conf_file = MOD_INFO.CONFIG_FILE

_control = None

def init():
    '''Mod's main entry point.  Called by WoT's built-in mod loader.'''
    global _control

    try:
        log.info('{} {} ({})'.format(MOD_INFO.NAME, MOD_INFO.VERSION_LONG, MOD_INFO.SUPPORT_URL))
        settings = Settings(conf_file, conf_base)
        _control = SpotMessanger(settings)
        
        log.debug('set key event handlers')
        if settings['ReloadConfigKey']:
            log.info('enabled ReloadConfigKey: key=\'{}\''.format(settings['ReloadConfigKey']))
            addKeyEventCallback(settings['ReloadConfigKey'], partial(_control.reloadConfig, conf_file, conf_base))
        else:
            log.info('disabled ReloadConfigKey')
        if settings['ActivationHotKey']:
            log.info('enabled ActivationHotKey: key=\'{}\''.format(settings['ActivationHotKey']))
            addKeyEventCallback(settings['ActivationHotKey'], _control.toggleActive)
        else:
            log.info('disabled ActivationHotKey')        
        g_playerEvents.onAvatarReady += _control.onBattleStart

    except:
        log.current_exception()

# referring to xvm/src/xpm/xvm_sounds/sixthSense.py 
@overrideMethod(SixthSenseIndicator, 'as_showS')
def _showSixthSenseIndicator(orig, *args, **kwargs):
    log.debug('activate sixth sense.')
    ret = orig(*args, **kwargs)
    try:
        _control.showSixthSenseIndicator()
    except:
        log.current_exception()
    return ret

@overrideMethod(game, 'handleKeyEvent')
def _handleKeyEvent(orig, *args, **kwargs):
    ret = orig(*args, **kwargs)
    try:
        handleKeyEvent(*args, **kwargs)
    except:
        log.current_exception()
    return ret
