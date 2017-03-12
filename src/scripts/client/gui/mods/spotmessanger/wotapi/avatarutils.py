
import BigWorld
from gui.battle_control import avatar_getter
from items.vehicles import getVehicleClass

from ..modconsts import VEHICLE_TYPE, BATTLE_TYPE
from ..logger import log


class _VehicleInfo(object):

    def __init__(self):
        self._typeDescriptor = avatar_getter.getVehicleTypeDescriptor()
    
    @property
    def name(self):
        return self._typeDescriptor.type.name
    
    @property
    def className(self):
        return getVehicleClass(self._typeDescriptor.type.compactDescr)

    @property
    def classAbbr(self):
        return VEHICLE_TYPE.LABELS[self.className]    


class _ArenaTypeInfo(object):

    def __init__(self):
        self._arenaType = avatar_getter.getArena().arenaType

    @property
    def name(self):
        return self._arenaType.name

    @property
    def geometryName(self):
        return self._arenaType.geometryName


class _ArenaGuiTypeInfo(object):

    def __init__(self):
        self._guiType = avatar_getter.getArena().guiType

    @property
    def id(self):
        return self._guiType

    @property
    def attrLabel(self):
        return BATTLE_TYPE.WOT_ATTR_NAME[self._guiType]
        
    @property
    def name(self):
        return BATTLE_TYPE.WOT_LABELS[self._guiType]

    @property
    def battleType(self):
        return BATTLE_TYPE.LABELS.get(self._guiType, 'others')


def getPlayer():
    return BigWorld.player()

def getVehicleInfo():
    return _VehicleInfo()

def getArenaTypeInfo():
    return _ArenaTypeInfo()

def getArenaGuiTypeInfo():
    return _ArenaGuiTypeInfo()

def isObserver():
    return BigWorld.player().isObserver()

def isPostMortem():
    return avatar_getter.getInputHandler().ctrlModeName == 'postmortem'

def isPlayerOnArena():
    if not hasattr(BigWorld.player(), 'arena'):
        return False
    return avatar_getter.isPlayerOnArena()

def getArena():
    if not hasattr(BigWorld.player(), 'arena'):
        return False
    return avatar_getter.getArena()

def getPos():
    return avatar_getter.getOwnVehiclePosition()

def getTeamAmount():
    arenaDP = BigWorld.player().guiSessionProvider.getArenaDP()
    team = avatar_getter.getPlayerTeam()
    return len([ v for v in arenaDP.getVehiclesInfoIterator() if v.team == team and v.isAlive() ])

def setForcedGuiControlMode(flag):
    avatar_getter.setForcedGuiControlMode(flag)
