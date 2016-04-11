# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU, Chirimen SEA

from functools import partial

import BigWorld
from gui.battle_control import g_sessionProvider
from messenger.gui.Scaleform.channels.bw_chat2.factories import BattleControllersFactory
from messenger.gui.Scaleform.channels.bw_chat2.battle_controllers import TeamChannelController, CommonChannelController, SquadChannelController
from chat_shared import CHAT_COMMANDS

from logger import log

CHANNEL_CLASS_LIST = {
    'common': CommonChannelController,
    'team': TeamChannelController,
    'squad': SquadChannelController
}

from messenger.m_constants import BATTLE_CHANNEL, PROTO_TYPE
from messenger.proto.interfaces import IEntityFindCriteria
from messenger.gui.scaleform.channels import BattleControllers

class _FindCriteria(IEntityFindCriteria):

    def __init__(self, channelSetting):
        super(_FindCriteria, self).__init__()
        self.__channelSetting = channelSetting

    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.BW_CHAT2 and channel.getProtoData().settings is self.__channelSetting

class IngameMessanger(object):
    _cooldDown = 0
    _controllers = None
    _commandFactory = None
    
    def __init__(self, commandDelay=0.5, textDelay=5.0):
        self._commandDelay = commandDelay
        self._textDelay = textDelay
        self._initChannelControllers()
        self._initCommandfactory()
    
    def _initChannelControllers(self):
        self._controllers = {}
        for controller in BattleControllersFactory().init():
            for k, v in CHANNEL_CLASS_LIST.iteritems():
                if isinstance(controller, v):
                    self._controllers[k] = controller
                    break
            else:
                log.warning('unknwon channel controller')
		
    def _initCommandfactory(self):
        self._commandFactory = g_sessionProvider.getChatCommands().proto.battleCmd
        if self._commandFactory is None:
            log.error('Commands factory is not defined')

    def _setCallback(self, delay, callback):
        currentTime = BigWorld.time()
        self._cooldDown = max(self._cooldDown, currentTime)
        diff = self._cooldDown - currentTime
        BigWorld.callback(diff, callback)
        self._cooldDown += delay

    def doPing(self, cellIdx):  
        delay = self._commandDelay
        command = self._commandFactory.createByCellIdx(cellIdx)
        self._setCallback(delay, partial(self._controllers['team'].sendCommand, command))
        return True

    def callHelp(self):
        delay = self._commandDelay
        command = self._commandFactory.createByName(CHAT_COMMANDS.HELPME.name())
        self._setCallback(delay, partial(self._controllers['team'].sendCommand, command))
        return True

    def sendText(self, channel, text):
        table = { 'team': BATTLE_CHANNEL.TEAM, 'squad': BATTLE_CHANNEL.SQUAD }
        criteria = _FindCriteria(table[channel])
        controller = BattleControllers().getControllerByCriteria(_FindCriteria(BATTLE_CHANNEL.TEAM))
        if controller:
            log.debug('found: BATTLE_CHANNEL.{}'.format(channel.upper()))
        if not self.has_channel(channel) or not text:
            log.info('channel not found: "{}"'.format(channel))
            return False
        delay = self._textDelay
        self._setCallback(delay, partial(self._controllers[channel]._broadcast, text))
        return True

    def sendTeam(self, text):
        log.debug('found: BATTLE_CHANNEL.TEAM')
        return self.sendText('team', text)

    def sendSquad(self, text):
        log.debug('found: BATTLE_CHANNEL.SQUAD')
        return self.sendText('squad', text)

    def has_channel(self, channel):
        return self._controllers.has_key(channel)

    def getKeys(self):
        return self._controllers.keys()

