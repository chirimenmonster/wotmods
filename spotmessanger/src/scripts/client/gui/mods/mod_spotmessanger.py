
from gui.Scaleform.Battle import Battle
from spotmessanger import log
from spotmessanger.events import registerEvent
from spotmessanger.const import MOD_INFO
from spotmessanger.SpotMessanger import SpotMessanger

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

@registerEvent(Battle, "_showSixthSenseIndicator")
def showSixthSenseIndicator(self, isShow):
    log.debug('acivate sixth sense!')
    SpotMessanger.showSixthSenseIndicator(self, isShow)
