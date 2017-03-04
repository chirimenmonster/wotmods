# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU, Chirimen SEA

from functools import partial

from messenger.m_constants import BATTLE_CHANNEL, PROTO_TYPE
from messenger.proto.interfaces import IEntityFindCriteria
from messenger.gui.scaleform.channels import BattleControllers
from chat_shared import CHAT_COMMANDS

from logger import log
from wotapis import Utils


class _Delay():
    command = 0.5
    text = 5.0


class _Criteria(IEntityFindCriteria):

    def __init__(self, channelSetting):
        super(_Criteria, self).__init__()
        self.__channelSetting = channelSetting

    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.BW_CHAT2 and channel.getProtoData().settings is self.__channelSetting


class DelayChatControl(object):
    
    def __init__(self):
        self._channelsCtrl = BattleControllers()
        self._channelsCtrl.init()
        self._wakeupTime = 0
        self._delay = _Delay()

    def setParam(self, commandDelay=0.5, textDelay=5.0):
        self._delay.command = commandDelay
        self._delay.text = textDelay
        
    def doPing(self, cellIdx):
        self._setCallback(self._delay.command, partial(_CBCommand.doPing, cellIdx))
        return True

    def callHelp(self):
        self._setCallback(self._delay.command, _CBCommand.callHelp)
        return True
    
    def sendTeam(self, text):
        log.debug('send to BATTLE_CHANNEL.TEAM')
        return self._sendText(BATTLE_CHANNEL.TEAM, text)

    def sendSquad(self, text):
        log.debug('send to BATTLE_CHANNEL.SQUAD')
        return self._sendText(BATTLE_CHANNEL.SQUAD, text)

    def getChannelLabels(self):
        labels = []
        for channel in BATTLE_CHANNEL.ALL:
            if self._channelsCtrl.getControllerByCriteria(_Criteria(channel)):
                labels.append(channel.name)
        return labels

    def _sendText(self, channel, text):
        channelCtrl = self._channelsCtrl.getControllerByCriteria(_Criteria(channel))
        if not channelCtrl:
            log.debug('channel: {} is not in {}'.format(channel.name, channelCtrl))
            return False
        log.debug('channel: {} is in {}'.format(channel.name, channelCtrl))
        self._setCallback(self._delay.text, partial(_CBCommand.sendText, channelCtrl, text))
        return True

    def _setCallback(self, delay, callback):
        currentTime = Utils.getTime()
        self._wakeupTime = max(self._wakeupTime, currentTime)
        Utils.setCallback(self._wakeupTime - currentTime, callback)
        self._wakeupTime += delay


class _CBCommand(object):

    @staticmethod
    def doPing(cellIdx):
        if not Utils.isPlayerOnArena():
            log.debug('avatar left arena')
            return
        Utils.setForcedGuiControlMode(True)
        Utils.getChatCommandCtrl().sendAttentionToCell(cellIdx)
        Utils.setForcedGuiControlMode(False)

    @staticmethod
    def callHelp():
        if not Utils.isPlayerOnArena():
            log.debug('avatar left arena')
            return
        Utils.getChatCommandCtrl().sendCommand(CHAT_COMMANDS.HELPME.name())

    @staticmethod
    def sendText(channelCtrl, text):
        if not Utils.isPlayerOnArena():
            log.debug('avatar left arena')
            return
        channelCtrl.sendMessage(text)
