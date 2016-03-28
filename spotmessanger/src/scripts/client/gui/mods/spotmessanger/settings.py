
import copy
import ResMgr
import log
from const import BATTLE_TYPE, COMMAND_TYPE, VEHICLE_TYPE
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
            log.info('available battletype tags: {}'.format(BATTLE_TYPE.LIST))
            self._settings['BattleType'] = {}
            for key, param in section['BattleTypeParameterList'].items():
                log.debug('key={}'.format(key))
                if key == 'BattleTypeParameter':
                    self._setBattleTypeSettings(param)
            log.info('found battletype settings: {}'.format(self._settings['BattleType'].keys()))

        return self._settings


    def _setBattleTypeSettings(self, section):
        log.debug('key: {}'.format(section.keys()))
        config = FileUtils.readElement(section, self._templateBattleType)
        config['CommandOrder'] = self._readElementList(section, 'CommandOrder', 'Command', COMMAND_TYPE.LIST)
        config['EnableVehicleType'] = self._readElementList(section, 'EnableVehicleType', 'VehicleType', VEHICLE_TYPE.LIST)
        for battleType in self._readElementList(section, 'AssignBattleType', 'BattleType', BATTLE_TYPE.LIST):
            self._settings['BattleType'][battleType] = config


    def _readElementList(self, section, parent, tag, items):
        list = []
        if not section.has_key(parent):
            log.warning('section "{}" is not found.'.format(parent))
            return list
        for key, value in section[parent].items():
            value = value.asString
            if key == tag:
                if value in items:
                    log.debug('found valid tag "{}" with valid item "{}", append to list.'.format(key, value))
                    list.append(value)
                else:
                    log.waring('found valid tag "{}" with invalid item "{}", available only {}'.format(key, value, items))                
            else:
                log.waring('found invalid tag "{}", available only "{}"'.format(key, tag))
        return list


st_control = Settings()
