
from constants import ARENA_GUI_TYPE, ARENA_GUI_TYPE_LABEL
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME

class BATTLE_TYPE:
    MAPPING = {
        'UNKNOWN':              'GlobalMap',
        'RANDOM':               'Random',
        'TRAINING':             'Training',
        'CYBERSPORT':           'TeamBattle',
        'FALLOUT':              'Fallout',
        'FALLOUT_CLASSIC':      'Fallout',
        'FALLOUT_MULTITEAM':    'Fallout',
        'SORTIE_2':             'Fortifications',
        'FORT_BATTLE_2':        'Fortifications',
        'RANKED':               'Ranked',
        'EPIC_RANDOM':          'EpicRandom',
        'EPIC_RANDOM_TRAINING': 'EpicRandomTraining',
        'EPIC_BATTLE':          'EpicBattle',
        'EPIC_TRAINING':        'EpicBattle',
    }
    WOT_ATTR_NAME = { v:k for k, v in vars(ARENA_GUI_TYPE).items() if isinstance(v, int) }
    WOT_LABELS = ARENA_GUI_TYPE_LABEL.LABELS
    LABELS = {}
    for id, name in WOT_ATTR_NAME.items():
        if name in MAPPING:
            LABELS[id] = MAPPING[name]
        else:
            LABELS[id] = 'others'
    LIST = list(set(LABELS.values())) + ['default']


class VEHICLE_TYPE:
    LABELS = {
        VEHICLE_CLASS_NAME.LIGHT_TANK: 'LT',
        VEHICLE_CLASS_NAME.MEDIUM_TANK: 'MT',
        VEHICLE_CLASS_NAME.HEAVY_TANK: 'HT',
        VEHICLE_CLASS_NAME.AT_SPG: 'TD',
        VEHICLE_CLASS_NAME.SPG: 'SPG'
    }
    LIST = list(set(LABELS.values()))


class COMMAND_TYPE:
    class LABELS:
        PING = 'ping'
        HELP = 'help'
        TEAMMSG = 'teammsg'
        SQUADMSG = 'squadmsg'
        UNSPOTTED = 'unspotted'
    LIST = [
        LABELS.PING,
        LABELS.HELP,
        LABELS.TEAMMSG,
        LABELS.SQUADMSG,
        LABELS.UNSPOTTED
    ]

