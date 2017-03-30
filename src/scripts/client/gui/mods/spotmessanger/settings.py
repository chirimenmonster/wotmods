import os
import copy
import pprint
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

PARAM_DEF = [
    [ PC_DEBUG,     'Debug',                'Bool',             ],
    [ PC_DEBUG,     'LogLevel',             LOGLEVEL.LIST,      ],
    [ PC_GLOBAL,    'ActiveByDefault',      'Bool',             ],
    [ PC_GLOBAL,    'NotifyCenter',         'Bool',             ],
    [ PC_GLOBAL,    'ActivationHotKey',     'String',           ],
    [ PC_GLOBAL,    'ReloadConfigKey',      'String',           ],
    [ PC_GLOBAL,    'ImSpotted',            'String',           ],
    [ PC_GLOBAL,    'DisableSystemMsg',     'String',           ],
    [ PC_GLOBAL,    'EnableSystemMsg',      'String',           ],
    [ PC_GLOBAL,    'CooldownMsg',          'String',           ],
    [ PC_FALLBACK,  'CooldownInterval',     'Float',            ],
    [ PC_FALLBACK,  'CommandDelay',         'Float',            ],
    [ PC_FALLBACK,  'TextDelay',            'Float',            ],
    [ PC_FALLBACK,  'MaxTeamAmount',        'Int',              ],
    [ PC_FALLBACK,  'MinTeamAmount',        'Int',              ],
    [ PC_OTHERS,    'AssignBattleType',     'List:BattleType',  ],
    [ PC_BATTLE,    'CommandOrder',         'List:Command',     ],
    [ PC_BATTLE,    'EnableVehicleType',    'List:VehicleType'  ],
    [ PC_OTHERS,    'BattleType',           BATTLE_TYPE.LIST,   ],
    [ PC_OTHERS,    'Command',              COMMAND_TYPE.LIST,  ],
    [ PC_OTHERS,    'VehicleType',          VEHICLE_TYPE.LIST,  ]
]

DEFAULT_GLOBAL_SETTINGS = {
    'Debug':            True,
    'LogLevel':         LOGLEVEL.LABELS.INFO,
    'ActiveByDefault':  True,
    'NotifyCenter':     True,
    'ActivationHotKey': 'KEY_F11',
    'ReloadConfigKey':  'KEY_NUMPAD4',
    'ImSpotted':        'An enemy has spotted me at {pos}.',
    'DisableSystemMsg': 'Sixth Sense Message disabled',
    'EnableSystemMsg':  'Sixth Sense Message enabled',
    'CooldownMsg':      'SpotMessanger: cooldown, rest {rest} sec.',
    'CooldownInterval': 60,
    'CommandDelay':     5.0,
    'TextDelay':        0.5,
    'MaxTeamAmount':    None,
    'MinTeamAmount':    1
}

DEFAULT_BATTLE_SETTINGS = {
    'CommandOrder':     [ COMMAND_TYPE.LABELS.HELP, COMMAND_TYPE.LABELS.TEAMMSG ]
}

PARAM_LIST_DEBUG    = [ v[INFO_TAG] for v in PARAM_DEF if v[INFO_CLASS] == PC_DEBUG ]
PARAM_LIST_GLOBAL   = [ v[INFO_TAG] for v in PARAM_DEF if v[INFO_CLASS] in (PC_GLOBAL, PC_FALLBACK) ]
PARAM_LIST_BATTLE   = [ v[INFO_TAG] for v in PARAM_DEF if v[INFO_CLASS] in (PC_BATTLE, PC_FALLBACK) ]

PARAM_INFO = { v[INFO_TAG]: v for v in PARAM_DEF }


class ChainDict(dict):
    _chain = None

    def __init__(self, dict, chain=None):
        super(ChainDict, self).__init__(dict)
        if chain is not None:
            self.setChain(chain)

    def __missing__(self, key):
        if isinstance(self._chain, dict):
            return self._chain[key]

    def setDict(self, dict):
        self.clear()
        self.update(dict)

    def setChain(self, chain):
        if not isinstance(chain, dict):
            raise TypeError
        self._chain = chain

    def getChain(self):
        return self._chain

    def getInfo(self, key, default='undef'):
        if key in self:
            value = self[key]
        else:
            try:
                value = 'inherits ({})'.format(self[key])
            except KeyError:
                value = default
        return value


class Settings(object):

    def __init__(self, file, prefix_list):
        for k in DEFAULT_GLOBAL_SETTINGS.keys() +  DEFAULT_BATTLE_SETTINGS.keys():
            assert k in PARAM_INFO, 'unknown default parameter: {}'.format(k)                
        self._defaultGlobal = ChainDict(DEFAULT_GLOBAL_SETTINGS)
        self._setLogLevel(self._defaultGlobal)
        self._paramGlobal = ChainDict({}, self._defaultGlobal)
        self._paramBattle = { 'default': [ ChainDict(DEFAULT_BATTLE_SETTINGS, self._paramGlobal) ] }
        self.readConfig(file, prefix_list)

    def __getitem__(self, key):
        return self._paramGlobal[key]

    def get(self, key, default=None):
        return self._paramGlobal.get(key, default)

    def _setLogLevel(self, config):
        log.setDebug(config['Debug'])
        log.setLogLevel(config['LogLevel'])
    
    def getParamsBattleType(self, battleType):
        if battleType in self._paramBattle:
            log.debug('parameter set for battle type "{}" is found'.format(battleType))
            return self._paramBattle[battleType]
        else:
            log.debug('parameter set for battle type "{}" is none, use "default"'.format(battleType))
            return self._paramBattle['default']

    def readConfig(self, file, prefix_list):
        for prefix in prefix_list:
            path = os.path.join(prefix, file)
            section = ResMgr.openSection(path, True)
            if section:
                log.info('read config file: {}'.format(ResMgr.resolveToAbsolutePath(path)))
                self._readConfig(section)
                break
        else:
            log.warning('cannot open config file: {}, use internal default settings.'.format(file))
        self.dumpSettings()
        return

    def _readConfig(self, section):
        self._paramGlobal.setDict(self._readSettings(section, PARAM_LIST_DEBUG))
        self._setLogLevel(self._paramGlobal)
        self._paramGlobal.update(self._readSettings(section, PARAM_LIST_GLOBAL))
        self._paramBattle = {}

        log.debug('available battletype tags: {}'.format(BATTLE_TYPE.LIST))

        for key, sectionBT in section['BattleTypeParameterList'].items():
            if key != 'BattleTypeParameter':
                log.warning('invalid tag "{}", "BattleTypeParameter" is only "BattleTypeParameter"\'s child'.format(key))
                continue
            if not sectionBT.has_key('AssignBattleType'):
                log.warning('missing "AssignBattleType" in section "{}".'.format(key))
                continue
            battleTypeList = self._readChild(sectionBT, 'AssignBattleType')
            log.debug('found AssignBattleType: {}'.format(battleTypeList))
            config = ChainDict(self._readSettings(sectionBT, PARAM_LIST_BATTLE), self._paramGlobal)
            for battleType in battleTypeList:
                if battleType not in self._paramBattle:
                    self._paramBattle[battleType] = []
                self._paramBattle[battleType].append(config)
        for configs in self._paramBattle.values():
            for i, config in enumerate(configs):
                config['index'] = i

    def dumpSettings(self):
        if not log.isDebug():
            return
        pp = pprint.PrettyPrinter()
        lines = []
        lines.append('_defaultGlobal:')
        lines.extend(pp.pformat(self._defaultGlobal).split('\n'))
        lines.append('_paramGlobal:')
        lines.extend(pp.pformat(self._paramGlobal).split('\n'))
        for key, param in self._paramBattle.items():
            for i, v in enumerate(param):
                lines.append('_paramBattle[\'{}\'][{}]:'.format(key, i))
                lines.extend(pp.pformat(v).split('\n'))
        for line in lines:
            log.debug(line)

    def _readSettings(self, section, paramList):
        config = {}
        for key in paramList:
            if section.has_key(key):
                config[key] = self._readChild(section, key)
        return config
        
    def _readChild(self, section, key):
        return self._readElement(section[key], PARAM_INFO[key][INFO_TYPE])

    def _readElement(self, element, attrType):
        RESMGR_ATTR = { 'Bool': 'asBool', 'Int': 'asInt', 'Float': 'asFloat', 'String': 'asString' }
        if isinstance(attrType, str) and attrType in RESMGR_ATTR:
            try:
                value = getattr(element, RESMGR_ATTR[attrType])
            except:
                log.current_exception()
                value = None
        elif isinstance(attrType, str) and attrType[:5] == 'List:':
            value = []
            childKey = attrType[5:]
            childType = PARAM_INFO[childKey][INFO_TYPE]
            for k, e in element.items():
                if k == childKey:
                    v = self._readElement(e, childType)
                    if v:
                        value.append(v)
                else:
                    log.warning('found invalid tag "{}", available only "{}"'.format(k, childKey))
        elif isinstance(attrType, list):
            try:
                value = element.asString
            except:
                log.current_exception()
            if value not in attrType:
                log.warning('found invalid item "{}", available only {}'.format(value, attrType))
                value = None
        else:
            if isinstance(attrType, str):
                raise AssertionError('unknown attr type string "{}"'.format(attrType))
            raise AssertionError('unknown attr type "{}"'.format(type(attrType)))
        return value
