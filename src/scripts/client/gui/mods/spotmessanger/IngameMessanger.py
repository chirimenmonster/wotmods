# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU, Chirimen SEA

from functools import partial

import BigWorld
from gui.battle_control import g_sessionProvider, avatar_getter
from messenger.m_constants import BATTLE_CHANNEL, PROTO_TYPE
from messenger.proto.interfaces import IEntityFindCriteria
from messenger.gui.scaleform.channels import BattleControllers
from chat_shared import CHAT_COMMANDS

from logger import log


class _Criteria(IEntityFindCriteria):

    def __init__(self, channelSetting):
        super(_Criteria, self).__init__()
        self.__channelSetting = channelSetting


    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.BW_CHAT2 and channel.getProtoData().settings is self.__channelSetting

        
class IngameMessanger(object):
    _cooldDown = 0
    _controllers = None
    _commandFactory = None

    
    def __init__(self):
        self._channelsCtrl = BattleControllers()
        self._channelsCtrl.init()
        self.setParam()


    def setParam(self, commandDelay=0.5, textDelay=5.0):
        self._commandDelay = commandDelay
        self._textDelay = textDelay
        

    def doPing(self, cellIdx):
        self._setCallback(self._commandDelay, partial(self._doPing, cellIdx))
        return True


    def callHelp(self):
        self._setCallback(self._commandDelay, self._callHelp)
    

    def sendText(self, channel, text):
        channelCtrl = self._channelsCtrl.getControllerByCriteria(_Criteria(channel))
        log.debug('found controller: {}'.format(channelCtrl))
        if not channelCtrl:
            log.debug('not found channel: {}'.format(channel.name))
            return False
        log.debug('found channel: {}'.format(channel.name))
        self._setCallback(self._textDelay, partial(self._sendText, channelCtrl, text))


    def sendTeam(self, text):
        log.debug('send to BATTLE_CHANNEL.TEAM')
        return self.sendText(BATTLE_CHANNEL.TEAM, text)


    def sendSquad(self, text):
        log.debug('send to BATTLE_CHANNEL.SQUAD')
        return self.sendText(BATTLE_CHANNEL.SQUAD, text)


    def getChannelLabels(self):
        labels = []
        for channel in BATTLE_CHANNEL.ALL:
            if self._channelsCtrl.getControllerByCriteria(_Criteria(channel)):
                labels.append(channel.name)
        return labels


    def _setCallback(self, delay, callback):
        currentTime = BigWorld.time()
        self._cooldDown = max(self._cooldDown, currentTime)
        diff = self._cooldDown - currentTime
        BigWorld.callback(diff, callback)
        self._cooldDown += delay

        
    def _doPing(self, cellIdx):
        avatar_getter.setForcedGuiControlMode(True)
        g_sessionProvider.shared.chatCommands.sendAttentionToCell(cellIdx)
        avatar_getter.setForcedGuiControlMode(False)


    def _callHelp(self):
        g_sessionProvider.shared.chatCommands.sendCommand(CHAT_COMMANDS.HELPME.name())


    def _sendText(self, channelCtrl, text):
        channelCtrl.sendMessage(text)

