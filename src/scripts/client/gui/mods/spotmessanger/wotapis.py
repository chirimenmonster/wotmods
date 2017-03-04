
import math

import BigWorld
from gui import SystemMessages
from gui.battle_control import avatar_getter, minimap_utils
from gui.battle_control.minimap_utils import MINIMAP_SIZE
from items.vehicles import getVehicleClass
from messenger import MessengerEntry

from modconsts import VEHICLE_TYPE, BATTLE_TYPE
from logger import log

class Utils:

    @staticmethod
    def getTime():
        return BigWorld.time()

    @staticmethod
    def getPlayer():
        return BigWorld.player()

    @staticmethod
    def isObserver():
        return BigWorld.player().isObserver()

    @staticmethod
    def isPostMortem():
        if avatar_getter.getInputHandler().ctrlModeName == 'postmortem':
            return True
        return False

    @staticmethod
    def isPlayerOnArena():
        if not hasattr(BigWorld.player(), 'arena'):
            return False
        return avatar_getter.isPlayerOnArena()

    @staticmethod
    def getPos():
        position = avatar_getter.getOwnVehiclePosition()
        return position

    @staticmethod
    def getTeamAmount():
        arenaDP = BigWorld.player().guiSessionProvider.getArenaDP()
        team = avatar_getter.getPlayerTeam()
        return len([ v for v in arenaDP.getVehiclesInfoIterator() if v.team == team and v.isAlive() ])

    @staticmethod
    def setCallback(time, function):
        return BigWorld.callback(time, function)
    
    @staticmethod
    def getSessionProvider():
        return BigWorld.player().guiSessionProvider
    
    @staticmethod
    def getChatCommandCtrl():
        return BigWorld.player().guiSessionProvider.shared.chatCommands

    @staticmethod
    def setForcedGuiControlMode(flag):
        avatar_getter.setForcedGuiControlMode(flag)
    
    @staticmethod
    def addClientMessage(message, isCurrentPlayer = False):
        MessengerEntry.g_instance.gui.addClientMessage(message, isCurrentPlayer)

    @staticmethod
    def addSystemMessage(message):
        SystemMessages.pushMessage(message)


class VehicleInfo(object):

    @property
    def typeDescriptor(self):
        return avatar_getter.getVehicleTypeDescriptor()
    
    @property
    def name(self):
        return self.typeDescriptor.type.name
    
    @property
    def className(self):
        return getVehicleClass(self.typeDescriptor.type.compactDescr)

    @property
    def classAbbr(self):
        return VEHICLE_TYPE.LABELS[self.className]


class ArenaInfo(object):

    @property
    def id(self):
        return avatar_getter.getArena().guiType

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
        localX = max(min(localX, MINIMAP_SIZE[0] - 0.1), 0)
        localY = max(min(localY, MINIMAP_SIZE[1] - 0.1), 0)
        return (localX, localY)

    @staticmethod
    def getCellIndexByPosition(position):      
        # ref.  xvm/src/xpm/xvm_main/utils.py: getMapSize() 
        bottomLeft, upperRight = avatar_getter.getArena().arenaType.boundingBox
        localPos = MinimapInfo.getLocalByPosition(position, bottomLeft, upperRight)
        cellIndex = MinimapInfo.makeCellIndex(localPos[0], localPos[1])
        cellName = MinimapInfo.getCellName(cellIndex)
        log.debug('bottomLeft = {}, upperRight = {}, spaceSize = {}'.format(bottomLeft, upperRight, upperRight - bottomLeft))
        log.debug('posion = {}, local = {}, cellIndex = {}, cellName = {}'.format(position, localPos, cellIndex, cellName))
        return cellIndex

