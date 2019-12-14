
import BigWorld
from chat_shared import CHAT_COMMANDS
from messenger import MessengerEntry
from messenger.m_constants import BATTLE_CHANNEL, PROTO_TYPE
from messenger.proto.interfaces import IEntityFindCriteria
from ..logger import log


class _Criteria(IEntityFindCriteria):

    def __init__(self, channelSetting):
        super(_Criteria, self).__init__()
        self.__channelSetting = channelSetting

    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.BW_CHAT2 and channel.getProtoData().settings is self.__channelSetting


def addClientMessage(message):
    MessengerEntry.g_instance.gui.addClientMessage(message)

def doPing(cellIdx):
    log.debug('doPing: {}'.format(cellIdx))
    _getChatCommandCtrl().sendAttentionToCell(cellIdx)

def callHelp():
    log.debug('callHelp')
    _getChatCommandCtrl().sendCommand(CHAT_COMMANDS.HELPME.name())

def sendTeamChat(text):
    log.debug('sendTeamChat: {}'.format(text))
    _sendChat(BATTLE_CHANNEL.TEAM, text)

def sendSquadChat(text):
    log.debug('sendSquadChat: {}'.format(text))
    _sendChat(BATTLE_CHANNEL.SQUAD, text)

def isExistSquadChannel():
    if _getChannelCtrl(BATTLE_CHANNEL.SQUAD):
        return True
    return False

def getChannelLabels():
    labels = []
    for channel in BATTLE_CHANNEL.ALL:
        if _getChannelCtrl(channel):
            labels.append(channel.name)
    return labels

def _sendChat(channel, text):
    channelCtrl = _getChannelCtrl(channel)
    channelCtrl.sendMessage(text)

def _getChannelCtrl(channel):
    return MessengerEntry.g_instance.gui.channelsCtrl.getControllerByCriteria(_Criteria(channel))

def _getChatCommandCtrl():
    return BigWorld.player().guiSessionProvider.shared.chatCommands
