
from debug_utils import LOG_CURRENT_EXCEPTION
from spotmessanger.SpotMessanger import SpotMessanger

def init():
    '''Mod's main entry point.  Called by WoT's built-in mod loader.'''
    try:
        print '[SpotMessanger] SpotMessanger development version'
        SpotMessanger.readConfig()
        if SpotMessanger.pluginEnable:
            print '[SpotMessanger] mod enable'
            SpotMessanger.run()
        
    except:
        LOG_CURRENT_EXCEPTION()
