
import BigWorld
from gui import SystemMessages


def getTime():
    return BigWorld.time()

def setCallback(time, function):
    return BigWorld.callback(time, function)

def addSystemMessage(message):
    SystemMessages.pushMessage(message)
