import os
import copy
import ResMgr
from logger import log, LOGLEVEL
from modconsts import BATTLE_TYPE, COMMAND_TYPE, VEHICLE_TYPE


PC_DEBUG    = 0
PC_GLOBAL   = 1
PC_FALLBACK = 2
PC_BATTLE   = 3
PC_OTHERS   = 4

INFO_CLASS      = 0 
INFO_TAG        = 1
INFO_TYPE       = 2
INFO_ISREQUIRED = 3
INFO_DEFAULT    = 4
INFO_CHILD      = 4
INFO_ENUM       = 5

PARAM_DEF = [
    [ PC_DEBUG,     'Debug',                'Bool',     False,  True                                ],
    [ PC_DEBUG,     'LogLevel',             'Enum',     False,  'info',         LOGLEVEL.LIST       ],
    [ PC_GLOBAL,    'ActiveByDefault',      'Bool',     False,  True                                ],
    [ PC_GLOBAL,    'NotifyCenter',         'Bool',     False,  True                                ],
    [ PC_GLOBAL,    'ActivationHotKey',     'String',   False,  'KEY_F11'                           ],
    [ PC_GLOBAL,    'ReloadConfigKey',      'String',   False,  'KEY_NUMPAD4'                       ],
    [ PC_GLOBAL,    'ImSpotted',            'String',   False,  'An enemy has spotted me at {pos}.'         ],
    [ PC_GLOBAL,    'DisableSystemMsg',     'String',   False,  'Sixth Sense Message disabled'              ],
    [ PC_GLOBAL,    'EnableSystemMsg',      'String',   False,  'Sixth Sense Message enabled'               ],
    [ PC_GLOBAL,    'CooldownMsg',          'String',   False,  'SpotMessanger: cooldown, rest {sec} sec.'  ],
    [ PC_FALLBACK,  'CooldownInterval',     'Float',    False,  60                                  ],
    [ PC_FALLBACK,  'CommandDelay',         'Float',    False,  0.5                                 ],
    [ PC_FALLBACK,  'TextDelay',            'Float',    False,  5                                   ],
    [ PC_FALLBACK,  'MaxTeamAmount',        'Int',      False,  None                                ],
    [ PC_FALLBACK,  'MinTeamAmount',        'Int',      False,  1                                   ],
    [ PC_BATTLE,    'AssignBattleType',     'List',     True,   'BattleType'                        ],
    [ PC_BATTLE,    'CommandOrder',         'List',     True,   'Command'                           ],
    [ PC_BATTLE,    'EnableVehicleType',    'List',     False,  'VehicleType'                       ],
    [ PC_OTHERS,    'BattleType',           'Enum',     False,  None,           BATTLE_TYPE.LIST    ],
    [ PC_OTHERS,    'Command',              'Enum',     False,  None,           COMMAND_TYPE.LIST   ],
    [ PC_OTHERS,    'VehicleType',          'Enum',     False,  None,           VEHICLE_TYPE.LIST   ]
]

DEFAULT_BATTLE_SETTINGS = {
    'default': [
        { 'CommandOrder':    [ 'help', 'teammsg' ] }
    ]
}

PARAM_LIST_DEBUG    = [ v[INFO_TAG] for v in PARAM_DEF if v[INFO_CLASS] == PC_DEBUG ]
PARAM_LIST_GLOBAL   = [ v[INFO_TAG] for v in PARAM_DEF if v[INFO_CLASS] in (PC_GLOBAL, PC_FALLBACK) ]
PARAM_LIST_FALLBACK = [ v[INFO_TAG] for v in PARAM_DEF if v[INFO_CLASS] == PC_FALLBACK ]
PARAM_LIST_BATTLE   = [ v[INFO_TAG] for v in PARAM_DEF if v[INFO_CLASS] in (PC_BATTLE, PC_FALLBACK) ]

PARAM_INFO = { v[INFO_TAG]: v for v in PARAM_DEF }


class _BattleSettings(object):

    def __init__(self, paramGlobal, paramBattle):
        self._paramGlobal = paramGlobal
        self._paramBattle = paramBattle

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, default=None, enableFallback=True):
        if enableFallback and key in PARAM_LIST_FALLBACK:
            value = self._paramBattle.get(key) or self._paramGlobal.get(key)
        elif key in PARAM_LIST_GLOBAL:
            value = self._paramGlobal.get(key)
        else:
            value = self._paramBattle.get(key)
        return value or default

    def getInfo(self, key, default='undef'):
        if key in PARAM_LIST_FALLBACK:
            value = self.get(key, None, enableFallback=False)
            if value is None:
                value = 'inherits ({})'.format(self.get(key, default, enableFallback=True))
        else:
            value = self.get(key, default)
        return value


class Settings(object):
    _paramGlobal = {}
    _paramBattle = {} 

    def __init__(self, file, prefix_list):
        for key in PARAM_LIST_DEBUG:
            self._paramGlobal[key] = PARAM_INFO[key][INFO_DEFAULT]
        self._setLogLevel()
        self.readConfig(file, prefix_list)

    def _setLogLevel(self):
        log.setDebug(self._paramGlobal['Debug'])
        log.setLogLevel(self._paramGlobal['LogLevel'])
    
    def get(self, key, default=None):
        return self._paramGlobal.get(key, default)

    def getParamsBattleType(self, battleType):
        paramBattleList = self._paramBattle.get(battleType, None)
        if paramBattleList:
            log.debug('parameter set for battle type "{}" is found'.format(battleType))
        else:
            log.debug('parameter set for battle type "{}" is none, use default'.format(battleType))
            paramBattleList = self._paramBattle['default']
        settings = [ _BattleSettings(self._paramGlobal, paramBattle) for paramBattle in paramBattleList ]
        return settings

    def readConfig(self, file, prefix_list=[ '' ]):
        self._paramGlobal = {}
        self._paramBattle = {} 

        for prefix in prefix_list:
            path = os.path.join(prefix, file)
            ResMgr.purge(path)
            section = ResMgr.openSection(path)
            if section:
                log.info('read config file: {}'.format(ResMgr.resolveToAbsolutePath(path)))
                break
        
        if section:
            self._paramGlobal.update(self._readSettings(section, PARAM_LIST_DEBUG, True))
            self._setLogLevel()
            self._paramGlobal.update(self._readSettings(section, PARAM_LIST_GLOBAL, True))

            log.debug('available battletype tags: {}'.format(BATTLE_TYPE.LIST))

            for key, sectionBT in section['BattleTypeParameterList'].items():
                if key != 'BattleTypeParameter':
                    log.warning('invalid tag "{}", "BattleTypeParameter" is only "BattleTypeParameter"\'s child'.format(key))
                    continue
                if not sectionBT.has_key('AssignBattleType'):
                    log.warning('miss "AssignBattleType" in section "{}".'.format(key))
                    continue
                battleTypeList = self._readElement(sectionBT['AssignBattleType'], 'AssignBattleType')
                log.debug('found AssignBattleType: {}'.format(battleTypeList))
                config = self._readSettings(sectionBT, PARAM_LIST_BATTLE, False)
                for battleType in battleTypeList:
                    self._paramBattle[battleType] = self._paramBattle.get(battleType, []) + [ config ]        
        else:
            log.warning('cannot open config file: {}, use internal default settings.'.format(file))
            for key in PARAM_LIST_DEBUG + PARAM_LIST_GLOBAL:
                self._paramGlobal[key] = PARAM_INFO[key][INFO_DEFAULT]
            self._paramBattle = DEFAULT_BATTLE_SETTINGS
        
        log.debug('_paramGlobal: {}'.format(self._paramGlobal))
        for key, param in self._paramBattle.items():
            for i, p in enumerate(param):
                log.debug('_paramBattle[\'{}\'][{}]: {}'.format(key, i, p))

    def _readSettings(self, section, paramList, withDefault=False):
        config = {}
        for key in paramList:
            if section.has_key(key):
                config[key] = self._readElement(section[key], key)
            elif withDefault and PARAM_INFO[key][INFO_TYPE] in [ 'Bool', 'Int', 'Float', 'String', 'Enum' ]:
                config[key] = PARAM_INFO[key][INFO_DEFAULT]
        return config

    def _readElement(self, element, key):
        keyType = PARAM_INFO[key][INFO_TYPE]
        resmgrAttr = { 'Bool': 'asBool', 'Int': 'asInt', 'Float': 'asFloat', 'String': 'asString' }
        #log.debug('read element as "{}" from section'.format(key))
        if keyType in resmgrAttr:
            try:
                return getattr(element, resmgrAttr[keyType])
            except:
                log.current_exception()
        elif keyType == 'Enum':
            try:
                v = element.asString
                e = PARAM_INFO[key][INFO_ENUM]
                if v in e:
                    return v
                else:
                    log.warning('found invalid item "{}", available only {}'.format(v, e))
                    return None
            except:
                log.current_exception()
        elif keyType == 'List':
            values = []
            child = PARAM_INFO[key][INFO_CHILD]
            for k, v in element.items():
                if k == child:
                    v = self._readElement(v, k)
                    if v:
                        values.append(v)
                else:
                    log.warning('found invalid tag "{}", available only "{}"'.format(k, child))
            return values
        return None
