
import copy
import ResMgr
from logger import log, LOGLEVEL
from modconsts import BATTLE_TYPE, COMMAND_TYPE, VEHICLE_TYPE


INFO_TAG = 0
INFO_TYPE = 1
INFO_ISREQUIRED = 2
INFO_DEFAULTVALUE = 3
INFO_CHILDTAG = 3
INFO_CHILDVALUES = 4
INFO_ENUMVALUES = 4

DEBUG_PARAM_DEF = [
    [ 'Debug',              'Bool',     False,  True            ],
    [ 'LogLevel',           'Enum',     False,  'info',         LOGLEVEL.LIST       ]
]

GLOBAL_PARAM_DEF = [
    [ 'ActiveByDefault',    'Bool',     False,  True            ],
    [ 'ActivationHotKey',   'String',   False,  'KEY_F11'       ],
    [ 'ReloadConfigKey',    'String',   False,  'KEY_NUMPAD4'   ],
    [ 'ImSpotted',          'String',   False,  'An enemy has spotted me at {pos}.'         ],
    [ 'DisableSystemMsg',   'String',   False,  'Sixth Sense Message disabled'              ],
    [ 'EnableSystemMsg',    'String',   False,  'Sixth Sense Message enabled'               ],
    [ 'CooldownMsg',        'String',   False,  'SpotMessanger: cooldown, rest {sec} sec.'  ]
]

FALLBACK_PARAM_DEF = [
    [ 'CooldownInterval',   'Float',    False,  60      ],
    [ 'CommandDelay',       'Float',    False,  0.5     ],
    [ 'TextDelay',          'Float',    False,  5       ],
    [ 'MaxTeamAmount',      'Int',      False,  None    ],
    [ 'MinTeamAmount',      'Int',      False,  1       ]
]

BATTLETYPE_PARAM_DEF = [
    [ 'AssignBattleType',   'List',     True,   'BattleType'    ],
    [ 'CommandOrder',       'List',     True,   'Command'       ],
    [ 'EnableVehicleType',  'List',     False,  'VehicleType'   ]
]

OTHER_PARAM_DEF = [
    [ 'BattleType',         'Enum',     False,  None,           BATTLE_TYPE.LIST    ],
    [ 'Command',            'Enum',     False,  None,           COMMAND_TYPE.LIST   ],
    [ 'VehicleType',        'Enum',     False,  None,           VEHICLE_TYPE.LIST   ]
]

DEFAULT_BATTLETYPE_SETTINGS = {
    'CommandOrder':    [ 'help', 'teammsg' ]
}

DEBUG_PARAM_LIST = [ v[INFO_TAG] for v in DEBUG_PARAM_DEF ]
GLOBAL_PARAM_LIST = [ v[INFO_TAG] for v in GLOBAL_PARAM_DEF + FALLBACK_PARAM_DEF ]
FALLBACK_PARAM_LIST = [ v[INFO_TAG] for v in FALLBACK_PARAM_DEF ]
BATTLETYPE_PARAM_LIST = [ v[INFO_TAG] for v in BATTLETYPE_PARAM_DEF + FALLBACK_PARAM_DEF ]

ALL_PARAM_INFO = { v[INFO_TAG]: v for v in DEBUG_PARAM_DEF + GLOBAL_PARAM_DEF + FALLBACK_PARAM_DEF + BATTLETYPE_PARAM_DEF + OTHER_PARAM_DEF }


class _BattleTypeSettings(object):

    def __init__(self, settings, battleType):
        self._paramGlobal = settings
        self._paramLocal = battleType

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, default=None, enableFallback=True):
        if key in FALLBACK_PARAM_LIST:
            value = self._paramLocal.get(key, None)
            if value is None and enableFallback:
                value = self._paramGlobal.get(key, None)
        elif key in GLOBAL_PARAM_LIST:
            value = self._paramGlobal.get(key, None)
        else:
            value = self._paramLocal.get(key, None)
        if value is None:
            value = default
        return value

    def getInfo(self, key, default='undef'):
        if key in FALLBACK_PARAM_LIST:
            value = self.get(key, None, enableFallback=False)
            if value is None:
                value = 'inherits ({})'.format(self.get(key, default, enableFallback=True))
        else:
            value = self.get(key, default)
        return value


class _Settings(object):
    _paramGlobal = {}
    _paramBattleType = {} 


    def get(self, key, default=None):
        return self._paramGlobal.get(key, default)


    def getParamsBattleType(self, battleType):
        params = self._paramBattleType.get(battleType, None)
        if params:
            log.debug('parameter set for battle type "{}" is found'.format(battleType))
        else:
            log.debug('parameter set for battle type "{}" is none, use default'.format(battleType))
            params = self._paramBattleType['default']
        settings = [ _BattleTypeSettings(self._paramGlobal, p) for p in params ]
        return settings


    def readConfig(self, file):
        debug = ALL_PARAM_INFO['Debug'][INFO_DEFAULTVALUE]
        log.setDebug(debug)

        self._paramGlobal = {}
        self._paramBattleType = {} 

        log.debug('config file: {}'.format(file))
        section = ResMgr.openSection(file)
        if section:
            for key in DEBUG_PARAM_LIST:
                self._setElementFromSettings(section, self._paramGlobal, key, True)
            log.setDebug(self._paramGlobal['Debug'])
            log.setLogLevel(self._paramGlobal['LogLevel'])

        log.debug('GLOBAL_PARAM_LIST: {}'.format(GLOBAL_PARAM_LIST))       
        if not section:
            log.warning('cannot open config file: {}, use internal default settings.'.format(file))
            for key in GLOBAL_PARAM_LIST:
                self._paramGlobal[key] = ALL_PARAM_INFO[key][INFO_DEFAULTVALUE]
            self._paramBattleType = { 'default': [ DEFAULT_BATTLETYPE_SETTINGS ] }
        else:
            self._setGlobalSettings(section)
            log.debug('available battletype tags: {}'.format(BATTLE_TYPE.LIST))
            for key, param in section['BattleTypeParameterList'].items():
                log.debug('found tag "{}" in BattleTypeParameterList'.format(key))
                if key == 'BattleTypeParameter':
                    self._setBattleTypeSettings(param)
            log.info('found battle type in settings: {}'.format(self._paramBattleType.keys()))

        log.debug('_paramGlobal: {}'.format(self._paramGlobal))
        for key, param in self._paramBattleType.items():
            for i, p in enumerate(param):
                log.debug('_paramBattleType[\'{}\'][{}]: {}'.format(key, i, p))

        
    def _setGlobalSettings(self, section):
        log.debug('found tags in global: {}'.format(section.keys()))
        for key in GLOBAL_PARAM_LIST:
            self._setElementFromSettings(section, self._paramGlobal, key, True)


    def _setBattleTypeSettings(self, section):
        log.debug('found tags in battletype: {}'.format(section.keys()))
        if not section.has_key('AssignBattleType'):
            log.warning('section "{}" is not found.'.format(key))
            return
        battleTypeList = self._readElement(section['AssignBattleType'], 'AssignBattleType')
        log.debug('found AssignBattleType: {}'.format(battleTypeList))
        config = {}
        for key in BATTLETYPE_PARAM_LIST:
            self._setElementFromSettings(section, config, key)
        for battleType in battleTypeList:
            if not self._paramBattleType.has_key(battleType):
                self._paramBattleType[battleType] = []
            self._paramBattleType[battleType].append(config)


    def _setElementFromSettings(self, section, config, key, withDefault=False):
        info = ALL_PARAM_INFO[key]
        if section.has_key(key):
            config[key] = self._readElement(section[key], key)
        else:
            if withDefault and info[INFO_TYPE] in [ 'Bool', 'Int', 'Float', 'String', 'Enum' ]:
                config[key] = info[INFO_DEFAULTVALUE]
            elif info[INFO_ISREQUIRED]:
                log.warning('section "{}" is not found.'.format(key))


    def _readElement(self, element, key):
        info = ALL_PARAM_INFO[key]
        resmgrAttr = { 'Bool': 'asBool', 'Int': 'asInt', 'Float': 'asFloat', 'String': 'asString' }
        #log.debug('read element as "{}" from section'.format(key))
        if info[INFO_TYPE] in resmgrAttr:
            try:
                return getattr(element, resmgrAttr[info[INFO_TYPE]])
            except:
                log.current_exception()
        elif info[INFO_TYPE] == 'Enum':
            try:
                v = element.asString
                if v in info[INFO_ENUMVALUES]:
                    return v
                else:
                    log.warning('found invalid item "{}", available only {}'.format(v, info[INFO_ENUMVALUES]))
                    return None
            except:
                log.current_exception()
        elif info[INFO_TYPE] == 'List':
            values = []
            for k, v in element.items():
                if k == info[INFO_CHILDTAG]:
                    v = self._readElement(v, info[INFO_CHILDTAG])
                    if v:
                        values.append(v)
                else:
                    log.warning('found invalid tag "{}", available only "{}"'.format(k, info[INFO_CHILDTAG]))
            return values
        return None


sm_settings = _Settings()
