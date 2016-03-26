
import copy
import ResMgr
import log
from ModUtils import FileUtils

class Settings(object):

    battleTypes = [ 'default', 'Random', 'Training', 'Company', 'CyberSport', 'Fortifications' ]
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
        'VehicleTypes': { 'LT': True, 'MT': True, 'HT': True, 'TD': True, 'SPG': True }
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
            for bt in cls.battleTypes:
                if section['BattleType'].has_key(bt):
                    cls._settings[bt] = FileUtils.readElement(section['BattleType'][bt], cls._templateBattleType, file)
        return cls._settings

