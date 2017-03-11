
import BigWorld
from gui.battle_control import avatar_getter


def getPlayer():
    return BigWorld.player()

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
