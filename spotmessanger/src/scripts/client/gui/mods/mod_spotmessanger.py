
from spotmessanger import log
from spotmessanger.constants import MOD_INFO
from spotmessanger.SpotMessanger import SpotMessanger

def init():
    '''Mod's main entry point.  Called by WoT's built-in mod loader.'''

    try:
        log.info(MOD_INFO.NAME + ' ' + MOD_INFO.VERSION_LONG)

        SpotMessanger.readConfig()
        if SpotMessanger.pluginEnable:
            log.info('mod enable')
            SpotMessanger.run()
        
    except:
        log.current_exception()
