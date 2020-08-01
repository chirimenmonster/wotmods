
import string

from gui.battle_control import avatar_getter, minimap_utils
from gui.battle_control.minimap_utils import MINIMAP_SIZE

from ..logger import log

MINIMAP_DIMENSION = 10.0

def makeCellIndex(localX, localY):
    limit = int(MINIMAP_DIMENSION) - 1
    column = min(limit, int(MINIMAP_DIMENSION * localX / MINIMAP_SIZE[0]))
    row = min(limit, int(MINIMAP_DIMENSION * localY / MINIMAP_SIZE[1]))
    return column * int(MINIMAP_DIMENSION) + row

def getCellName(cellIndex):
    column, row = divmod(cellIndex, int(MINIMAP_DIMENSION))
    rowName = 'ABCDEFGHJK'[row]
    columnName = '1234567890'[column]
    return rowName + columnName

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

def getCellNameByPosition(position):
    cellIndex = getCellIndexByPosition(position)
    return getCellName(cellIndex)
