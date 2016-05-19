
import copy
import ResMgr
from logger import log
from modconsts import BATTLE_TYPE, COMMAND_TYPE, VEHICLE_TYPE


INFO_TAG = 0
INFO_TYPE = 1
INFO_ISREQUIRED = 2
INFO_DEFAULTVALUE = 3
INFO_CHILDTAG = 3
INFO_CHILDVALUES = 4

GLOBAL_PARAM_DEF = [
    [ 'Debug',              'Bool',     False,  True            ],
    [ 'ActiveByDefault',    'Bool',     False,  True            ],
    [ 'ActivationHotKey',   'String',   False,  'KEY_F11'       ],
    [ 'ReloadConfigKey',    'String',   False,  'KEY_NUMPAD4'   ],
    [ 'ImSpotted',          'String',   False,  'An enemy has spotted me at {pos}.'         ],
    [ 'DisableSystemMsg',   'String',   False,  'Sixth Sense Message disabled'              ],
    [ 'EnableSystemMsg',    'String',   False,  'Sixth Sense Message enabled'               ],
    [ 'CooldownMsg',        'String',   False,  'SpotMessanger: cooldown, rest {sec} sec.'  ]
]

FALLBACK_PARAM_DEF = [
    [ 'CooldownInterval',   'Float',    False,  60  ],
    [ 'CommandDelay',       'Float',    False,  0.5 ],
    [ 'TextDelay',          'Float',    False,  5   ]
]

BATTLETYPE_PARAM_DEF = [
    [ 'AssignBattleType',   'List',     True,   'BattleType',   BATTLE_TYPE.LIST    ],
    [ 'CommandOrder',       'List',     True,   'Command',      COMMAND_TYPE.LIST   ],
    [ 'MaxTeamAmount',      'Int',      False   ],
    [ 'EnableVehicleType',  'List',     False,  'VehicleType',  VEHICLE_TYPE.LIST   ],
    [ 'BattleType',         'String',   False   ],
    [ 'Command',            'String',   False   ],
    [ 'VehicleType',        'String',   False   ]
]

DEFAULT_BATTLETYPE_SETTINGS = {
    'CommmandOrder':    [ 'help', 'teammsg' ]
}

GLOBAL_PARAM_LIST = [ v[INFO_TAG] for v in GLOBAL_PARAM_DEF + FALLBACK_PARAM_DEF ]
FALLBACK_PARAM_LIST = [ v[INFO_TAG] for v in FALLBACK_PARAM_DEF ]

ALL_PARAM_INFO = { v[INFO_TAG]: v for v in GLOBAL_PARAM_DEF + FALLBACK_PARAM_DEF + BATTLETYPE_PARAM_DEF }
BATTLETYPE_PARAM_INFO = { v[INFO_TAG]: v for v in BATTLETYPE_PARAM_DEF + FALLBACK_PARAM_DEF }


class _Settings(object):
    _settings = {}

    def get(self, key, default=None):
        return self._settings.get(key, default)


    def getParamsBattleType(self, battleType):
        params = self._settings['BattleType'].get(battleType, None)
        if params:
            log.debug('parameter set for battle type "{}" is found'.format(battleType))
        else:
            log.debug('parameter set for battle type "{}" is none, use default'.format(battleType))
            params = self._settings['BattleType']['default']
        return params


    def readConfig(self, file):
        debug = ALL_PARAM_INFO['Debug'][INFO_DEFAULTVALUE]
        log.setDebug(debug)

        log.info('config file: {}'.format(file))

        section = ResMgr.openSection(file)
        if section:
            debug = section.readBool('Debug', debug)
            log.setDebug(debug)

        log.debug('GLOBAL_PARAM_LIST: {}'.format(GLOBAL_PARAM_LIST))
        
        if not section:
            log.warning('cannot open config file: {}'.format(file))
            config = {}
            for key in GLOBAL_PARAM_LIST:
                config[key] = ALL_PARAM_INFO[key][INFO_DEFAULTVALUE]
            config['BattleType']['default'] = [ DEFAULT_BATTLETYPE_SETTINGS ]
            self._settings = config
        else:
            self._setGlobalSettings(section)
            log.debug('available battletype tags: {}'.format(BATTLE_TYPE.LIST))
            for key, param in section['BattleTypeParameterList'].items():
                log.debug('found tag "{}" in BattleTypeParameterList'.format(key))
                if key == 'BattleTypeParameter':
                    self._setBattleTypeSettings(param)
            log.info('found battle type in settings: {}'.format(self._settings['BattleType'].keys()))

        log.debug('settings = {}'.format(self._settings))
        return self._settings

        
    def _setGlobalSettings(self, section):
        log.debug('found tags in global: {}'.format(section.keys()))
        config = {}
        for key in GLOBAL_PARAM_LIST:
            self._setElementFromSettings(section, config, key, True)
        self._settings = config
        self._settings['BattleType'] = {}


    def _setBattleTypeSettings(self, section):
        log.debug('found tags in battletype: {}'.format(section.keys()))
        config = {}
        for key in [ 'CommandOrder', 'EnableVehicleType', 'MaxTeamAmount' ] + FALLBACK_PARAM_LIST:
            self._setElementFromSettings(section, config, key)
        battleTypeList = self._readElement(section['AssignBattleType'], 'AssignBattleType')
        log.debug('found AssignBattleType: {}'.format(battleTypeList))
        for battleType in self._readElement(section['AssignBattleType'], 'AssignBattleType'):
            if self._settings['BattleType'].has_key(battleType):
                self._settings['BattleType'][battleType].append(config)
            else:
                self._settings['BattleType'][battleType] = [ config ]


    def _setElementFromSettings(self, section, config, key, withDefault=False):
        info = ALL_PARAM_INFO[key]
        if section.has_key(key):
            config[key] = self._readElement(section[key], key)
        else:
            if withDefault and info[INFO_TYPE] in [ 'Bool', 'Int', 'Float', 'String' ]:
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
        elif info[INFO_TYPE] in [ 'List' ]:
            values = []
            for k, v in element.items():
                if k in info[INFO_CHILDTAG]:
                    v = self._readElement(v, info[INFO_CHILDTAG])
                    if v in info[INFO_CHILDVALUES]:
                        #log.debug('found valid item "{}", append to list.'.format(v))
                        values.append(v)
                    else:
                        log.warning('found invalid item "{}", available only {}'.format(v, info[INFO_CHILDVALUES]))
                else:
                    log.warning('found invalid tag "{}", available only "{}"'.format(k, info[INFO_CHILDTAG]))
            return values
        return None


sm_settings = _Settings()
