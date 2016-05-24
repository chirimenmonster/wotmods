# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU, Chirimen SEA

from functools import partial

import BigWorld
from gui.battle_control import g_sessionProvider
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
        
    def _setCallback(self, delay, callback):
        currentTime = BigWorld.time()
        self._cooldDown = max(self._cooldDown, currentTime)
        diff = self._cooldDown - currentTime
        BigWorld.callback(diff, callback)
        self._cooldDown += delay

    def doPing(self, cellIdx):
        controller = g_sessionProvider.getChatCommands()
        self._setCallback(self._commandDelay, partial(controller.sendAttentionToCell, cellIdx))
        return True

    def callHelp(self):
        controller = g_sessionProvider.getChatCommands()
        self._setCallback(self._commandDelay, partial(controller.sendCommand, CHAT_COMMANDS.HELPME.name()))
        return True

    def sendText(self, channel, text):
        controller = self._channelsCtrl.getControllerByCriteria(_Criteria(channel))
        log.debug('found controller: {}'.format(controller))
        if not controller:
            log.debug('not found channel: {}'.format(channel.name))
            return False
        log.debug('found channel: {}'.format(channel.name))
        self._setCallback(self._textDelay, partial(controller.sendMessage, text))
        return True

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

