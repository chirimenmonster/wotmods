
import BigWorld
from items.vehicles import getVehicleClass
from modconsts import VEHICLE_TYPE, BATTLE_TYPE


class Utils(object):

    @classmethod
    def getTime(cls):
        return BigWorld.time()

    @classmethod
    def getPlayer(cls):
        return BigWorld.player()


class VehicleInfo(object):

    def __init__(self, vehicleID=None, player=None):
        if not vehicleID:
            if not player:
                player = BigWorld.player()
            vehicleID = player.playerVehicleID
        self._vehicle = BigWorld.entity(vehicleID)
        self._vehicleCompactDescr = self._vehicle.typeDescriptor.type.compactDescr
    
    @property
    def name(self):
        return self._vehicle.typeDescriptor.type.name
    
    @property
    def className(self):
        return getVehicleClass(self._vehicleCompactDescr)

    @property
    def classAbbr(self):
        return VEHICLE_TYPE.LABELS[self.className]


class ArenaInfo(object):

    def __init__(self, player=None):
        if not player:
            player = BigWorld.player()
        self._arenaType = player.arena.guiType

    @property
    def id(self):
        return self._arenaType

    @property
    def attrLabel(self):
        return BATTLE_TYPE.WOT_ATTR_NAME[self._arenaType]
        
    @property
    def name(self):
        return BATTLE_TYPE.WOT_LABELS[self._arenaType]

    @property
    def battleType(self):
        return BATTLE_TYPE.LABELS.get(self._arenaType, 'others')

