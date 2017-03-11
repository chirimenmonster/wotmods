
import math

from gui.battle_control import avatar_getter, minimap_utils
from gui.battle_control.minimap_utils import MINIMAP_SIZE

from ..logger import log


def makeCellIndex(localX, localY):
    return int(minimap_utils.makeCellIndex(localX, localY))

def getCellName(cellIndex):
    return minimap_utils.getCellName(cellIndex)

def getLocalByPosition(position, bottomLeft, upperRight):
    spaceSize = upperRight - bottomLeft
    centerPos = (upperRight + bottomLeft) * 0.5
    localX = (position[0] - centerPos[0]) / spaceSize[0] * MINIMAP_SIZE[0] + MINIMAP_SIZE[0] * 0.5
    localY = -(position[2] - centerPos[1]) / spaceSize[1] * MINIMAP_SIZE[1] + MINIMAP_SIZE[1] * 0.5
    localX = max(min(localX, MINIMAP_SIZE[0] - 0.1), 0)
    localY = max(min(localY, MINIMAP_SIZE[1] - 0.1), 0)
    return (localX, localY)

def getCellIndexByPosition(position):      
    # ref.  xvm/src/xpm/xvm_main/utils.py: getMapSize() 
    bottomLeft, upperRight = avatar_getter.getArena().arenaType.boundingBox
    localPos = getLocalByPosition(position, bottomLeft, upperRight)
    cellIndex = makeCellIndex(localPos[0], localPos[1])
    cellName = getCellName(cellIndex)
    log.debug('bottomLeft = {}, upperRight = {}, spaceSize = {}'.format(bottomLeft, upperRight, upperRight - bottomLeft))
    log.debug('posion = {}, local = {}, cellIndex = {}, cellName = {}'.format(position, localPos, cellIndex, cellName)) 
    return cellIndex
