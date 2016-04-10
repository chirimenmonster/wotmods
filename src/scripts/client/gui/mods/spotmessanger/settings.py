
import copy
import ResMgr
from logger import log
from modconsts import BATTLE_TYPE, COMMAND_TYPE, VEHICLE_TYPE
from ModUtils import FileUtils

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
}

FALLBACK_PARAM_LIST = [
    'CooldownInterval',
    'CommandDelay',
    'TextDelay'
]

GLOBAL_PARAM_LIST = [ k for k in _templateGlobal.keys() if not k in FALLBACK_PARAM_LIST ]

class _Settings(object):
    _settings = {}
    _currentContext = {}

    def get(self, key, default=None):
        if key in GLOBAL_PARAM_LIST:
            return self._settings.get(key, default)
        if self._currentContext.has_key(key):
            return self._currentContext.get(key, default)
        if key in FALLBACK_PARAM_LIST:
            return self._settings.get(key, default)
        return default

    def setBattleType(self, battleType):
        param = self._settings['BattleType'].get(battleType, None)
        if param:
            log.debug('parameter set for battle type "{}" is found'.format(battleType))
        else:
            param = self._settings['BattleType']['default']
            log.debug('parameter set for battle type "{}" is none, use default'.format(battleType))
        self._currentContext = param
            
    def readConfig(self, file):
        log.info('config file: {}'.format(file))
        section = ResMgr.openSection(file)

        log.debug('GLOBAL_PARAM_LIST: {}'.format(GLOBAL_PARAM_LIST))
        log.debug('FALLBACK_PARAM_LIST: {}'.format(FALLBACK_PARAM_LIST))
        
        debug = _templateGlobal['Debug']
        if section:
            debug = section.readBool('Debug', debug)
        log.setDebug(debug)
        
        if not section:
            log.warning('cannot open config file: {}'.format(file))
            self._settings = copy.copy(_templateGlobal)
            self._settings['default'] = copy.copy(_templateBattleType)
        else:
            self._settings = FileUtils.readElement(section, _templateGlobal, file)
            self._settings['BattleType'] = {}
            log.info('available battletype tags: {}'.format(BATTLE_TYPE.LIST))
            for key, param in section['BattleTypeParameterList'].items():
                log.debug('key={}'.format(key))
                if key == 'BattleTypeParameter':
                    self._setBattleTypeSettings(param)
            log.info('found battletype settings: {}'.format(self._settings['BattleType'].keys()))

        log.debug('settings = {}'.format(self._settings))
        return self._settings


    def _setBattleTypeSettings(self, section):
        log.debug('key: {}'.format(section.keys()))
        config = FileUtils.readElement(section, _templateBattleType)
        config['CommandOrder'] = self._readElementList(section, 'CommandOrder', 'Command', COMMAND_TYPE.LIST)
        config['EnableVehicleType'] = self._readElementList(section, 'EnableVehicleType', 'VehicleType', VEHICLE_TYPE.LIST)
        for key in FALLBACK_PARAM_LIST:
            value = self._readElementAsFloat(section, key)
            if value:
                config[key] = value
        for battleType in self._readElementList(section, 'AssignBattleType', 'BattleType', BATTLE_TYPE.LIST):
            self._settings['BattleType'][battleType] = config

    def _readElementAsFloat(self, section, key):
        if not section.has_key(key):
            return None
        try:
            value = section[key].asFloat
            return value
        except:
            log.current_exception()

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
                    log.waring('found valid tag "{}", but invalid item "{}", available only {}'.format(key, value, items))
            else:
                log.waring('found invalid tag "{}", available only "{}"'.format(key, tag))
        return list


sm_settings = _Settings()
