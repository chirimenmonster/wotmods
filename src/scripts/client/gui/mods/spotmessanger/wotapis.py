
import math

import BigWorld
from gui import SystemMessages
from gui.battle_control import avatar_getter
from items.vehicles import getVehicleClass
from messenger import MessengerEntry

from modconsts import VEHICLE_TYPE, BATTLE_TYPE
from logger import log

class Utils(object):

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
    def getArena():
        if not hasattr(BigWorld.player(), 'arena'):
            return False
        return avatar_getter.getArena()

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
    def setForcedGuiControlMode(flag):
        avatar_getter.setForcedGuiControlMode(flag)
    
    @staticmethod
    def addClientMessage(message):
        MessengerEntry.g_instance.gui.addClientMessage(message)

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
