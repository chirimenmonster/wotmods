
import math
import BigWorld
from items.vehicles import getVehicleClass
from gui.battle_control import avatar_getter, arena_info, minimap_utils
from gui.battle_control.minimap_utils import MINIMAP_SIZE

from modconsts import VEHICLE_TYPE, BATTLE_TYPE
from logger import log

class Utils(object):

    @classmethod
    def getTime(cls):
        return BigWorld.time()

    @classmethod
    def getPlayer(cls):
        return BigWorld.player()

    @classmethod
    def getPos(cls, avatar = None):
        if not avatar:
            avatar = cls.getPlayer()
        position = BigWorld.entities[avatar.playerVehicleID].position
        log.debug('position = {}'.format(position))
        return position


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


class MinimapInfo(object):

    @staticmethod
    def makeCellIndex(localX, localY):
        return int(minimap_utils.makeCellIndex(localX, localY))


    @staticmethod
    def getCellName(cellIndex):
        return minimap_utils.getCellName(cellIndex)

        
    @staticmethod
    def getLocalByPosition(position, bottomLeft, upperRight):
        spaceSize = upperRight - bottomLeft
        centerPos = (upperRight + bottomLeft) * 0.5
        localX = (position[0] - centerPos[0]) / spaceSize[0] * MINIMAP_SIZE[0] + MINIMAP_SIZE[0] * 0.5
        localY = -(position[2] - centerPos[1]) / spaceSize[1] * MINIMAP_SIZE[1] + MINIMAP_SIZE[1] * 0.5
        return (localX, localY)


    @classmethod
    def getCellIndexByPosition(cls, position):      
        arenaType = arena_info.getArenaType()
        bottomLeft, upperRight = arenaType.boundingBox
        localPos = cls.getLocalByPosition(position, bottomLeft, upperRight)
        cellIndex = cls.makeCellIndex(localPos[0], localPos[1])
        cellName = cls.getCellName(cellIndex)
        log.debug('bottomLeft = {}, upperRight = {}, spaceSize = {}'.format(bottomLeft, upperRight, upperRight - bottomLeft))
        log.debug('posion = {}, local = {}, cellIndex = {}, cellName = {}'.format(position, localPos, cellIndex, cellName))
        return cellIndex

