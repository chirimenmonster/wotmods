
import copy
import ResMgr
import log
from const import BATTLE_TYPE, COMMAND_TYPE
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
        'MaxTeamAmount': 0,
        'VehicleTypes': { 'LT': True, 'MT': True, 'HT': True, 'TD': True, 'SPG': True },
        'CooldownInterval': 0,
        'TextDelay': 0.0,
        'CommandDelay': 0.0
    }
    _settings = {}
	
    def readConfig(self, file):
        log.info('config file: {}'.format(file))
        section = ResMgr.openSection(file)
        if not section:
            log.warning('cannot open config file: {}'.format(file))
            self._settings = copy.copy(self._templateGlobal)
            self._settings['default'] = self._templateBattleType
        else:
            if section['Debug'].asString.lower() == 'true':
                log.flgDebugMsg = True
            elif section['Debug'].asString.lower() == 'false':
                log.flgDebugMsg = False
            self._settings = FileUtils.readElement(section, self._templateGlobal, file)
            log.info('available battletype tags: {}'.format(BATTLE_TYPE.LIST + ['default']))
            self._settings['BattleType'] = {}
            for key, param in section['BattleTypeParameterList'].items():
                log.debug('key={}'.format(key))
                if key == 'BattleTypeParameter':
                    self._readBattleTypeSettings(param)
            log.info('found battletype settings: {}'.format(self._settings['BattleType'].keys()))

        return self._settings


    def _readBattleTypeSettings(self, section):
        battleTypeList = []
        commandOrder = []
        log.debug('key: {}'.format(section.keys()))
        for key, value in section['AssignBattleType'].items():
            value = value.asString
            log.debug('check key and value for "AssignBattleType": {}={}'.format(key, value))
            if key == 'BattleType' and value in BATTLE_TYPE.LIST + ['default']:
                log.debug('valid BattleType: {}'.format(value))
                battleTypeList.append(value)
        for key, value in section['CommandOrder'].items():
            value = value.asString
            log.debug('check key and value for "CommandOrder": {}={}'.format(key, value))
            if key == 'Command' and value in COMMAND_TYPE.LIST:
                log.debug('valid Command: {}'.format(value))
                commandOrder.append(value)           
        config = FileUtils.readElement(section, self._templateBattleType)
        config['CommandOrder'] = commandOrder
        for battleType in battleTypeList:
            self._settings['BattleType'][battleType] = config


st_control = Settings()
