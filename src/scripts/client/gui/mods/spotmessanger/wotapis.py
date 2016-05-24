
import BigWorld
from items.vehicles import getVehicleClass
from gui.battle_control import avatar_getter
from modconsts import VEHICLE_TYPE, BATTLE_TYPE


class Utils(object):

    @classmethod
    def getTime(cls):
        return BigWorld.time()

    @classmethod
    def getPlayer(cls):
        return BigWorld.player()


class VehicleInfo(object):

    def __init__(self, avatar=None):
        self._typeDescriptor = avatar_getter.getVehicleTypeDescriptor(avatar)
    
    @property
    def name(self):
        return self._typeDescriptor.type.name
    
    @property
    def className(self):
        return getVehicleClass(self._typeDescriptor.type.compactDescr)

    @property
    def classAbbr(self):
        return VEHICLE_TYPE.LABELS[self.className]


class ArenaInfo(object):

    def __init__(self, avatar=None):
        self._arena = avatar_getter.getArena()

    @property
    def id(self):
        return self._arena.guiType

    @property
    def attrLabel(self):
        return BATTLE_TYPE.WOT_ATTR_NAME[self.id]
        
    @property
    def name(self):
        return BATTLE_TYPE.WOT_LABELS[self.id]

    @property
    def battleType(self):
        return BATTLE_TYPE.LABELS.get(self.id, 'others')

