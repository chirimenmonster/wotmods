
import math

import BigWorld
from gui import SystemMessages
from gui.battle_control import avatar_getter
from items.vehicles import getVehicleClass
from messenger import MessengerEntry

from modconsts import VEHICLE_TYPE, BATTLE_TYPE
from logger import log


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
