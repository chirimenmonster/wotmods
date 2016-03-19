
from constants import ARENA_GUI_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME

class MOD_INFO:
    NAME ='SpotMessanger'
    VERSION = 'dev'
    VERSION_LONG = 'development version'

class BATTLE_TYPE:
    LABELS = {
        ARENA_GUI_TYPE.UNKNOWN: 'Unknown',	
        ARENA_GUI_TYPE.RANDOM: 'Random',
        ARENA_GUI_TYPE.TRAINING: 'Training',
        ARENA_GUI_TYPE.COMPANY: 'Company',
        ARENA_GUI_TYPE.TUTORIAL: 'Tutorial',
        ARENA_GUI_TYPE.CYBERSPORT: 'CyberSport',
        ARENA_GUI_TYPE.FALLOUT: 'Fallout',
        ARENA_GUI_TYPE.EVENT_BATTLES: 'EventBattles',
        ARENA_GUI_TYPE.SORTIE: 'Fortifications',
        ARENA_GUI_TYPE.FORT_BATTLE: 'Fortifications',
        ARENA_GUI_TYPE.RATED_CYBERSPORT: 'CyberSport',
        ARENA_GUI_TYPE.RATED_SANDBOX: 'Sandbox',
        ARENA_GUI_TYPE.SANDBOX: 'Sandbox',
        ARENA_GUI_TYPE.FALLOUT_CLASSIC: 'Fallout',
        ARENA_GUI_TYPE.FALLOUT_MULTITEAM: 'Fallout'
	}

class VEHICLE_TYPE:
    LABELS = {
        VEHICLE_CLASS_NAME.LIGHT_TANK: 'LT',
        VEHICLE_CLASS_NAME.MEDIUM_TANK: 'MD',
        VEHICLE_CLASS_NAME.HEAVY_TANK: 'HT',
        VEHICLE_CLASS_NAME.AT_SPG: 'TD',
        VEHICLE_CLASS_NAME.SPG: 'SPG'
	}

