
import copy
import ResMgr
import log
from const import BATTLE_TYPE
from ModUtils import FileUtils

class Settings(object):

    _templateGlobal = {
        'Debug': True,
        'ActiveByDefault': True,
        'ActivationHotKey': 'KEY_F11',
        'ReloadConfigKey': 'KEY_NUMPAD4',
        'ImSpotted': 'An enemy has spotted me at {pos}.',
        'DisableSystemMsg': 'Sixth Sense Message disabled',
        'EnableSystemMsg': 'Sixth Sense Message enabled',
        'CooldownInterval': 60,
        'CooldownMsg': 'SpotMessanger: cooldown, rest {sec} sec.',
        'TextDelay': 0.5,
        'CommandDelay': 5
    }
    _templateBattleType = {
        'Order': [ 'ping', 'help', 'teammsg' ],
        'MaxTeamAmount': 0,
        'VehicleTypes': { 'LT': True, 'MT': True, 'HT': True, 'TD': True, 'SPG': True },
        'CooldownInterval': 0,
        'TextDelay': 0.0,
        'CommandDelay': 0.0
    }
    _settings = {}
	
    @classmethod
    def readConfig(cls, file):
        log.debug('read config file: {}'.format(file))
        section = ResMgr.openSection(file)
        if not section:
            log.warning('cannot open config file: {}'.format(file))
            cls._settings = copy.copy(cls._templateGlobal)
            cls._settings['default'] = cls._templateBattleType
        else:
            log.info('config found: {}'.format(file))
            cls._settings = FileUtils.readElement(section, cls._templateGlobal, file)
            print 'available battle tags: ', BATTLE_TYPE.LIST + ['default']
            for bt in BATTLE_TYPE.LIST + ['default']:
                if section['BattleType'].has_key(bt):
                    cls._settings[bt] = FileUtils.readElement(section['BattleType'][bt], cls._templateBattleType, file)
        return cls._settings

