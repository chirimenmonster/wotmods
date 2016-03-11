
from debug_utils import LOG_CURRENT_EXCEPTION
from spotmessanger.SpotMessanger_plugin.SpotMessanger import SpotMessanger

def init():
    '''Mod's main entry point.  Called by WoT's built-in mod loader.'''
    try:
        print 'SpotMessanger DEV'
        SpotMessanger.readConfig()
        if SpotMessanger.pluginEnable:
            print '---> Loading SpotMessanger'
            SpotMessanger.run()
        
    except:
        LOG_CURRENT_EXCEPTION()
