# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU

from functools import partial

import BigWorld
from gui.battle_control import g_sessionProvider
from messenger.gui.Scaleform.channels.bw_chat2.factories import BattleControllersFactory
from messenger.gui.Scaleform.channels.bw_chat2.battle_controllers import TeamChannelController, CommonChannelController, SquadChannelController
from chat_shared import CHAT_COMMANDS

from logger import log

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
        controllers = BattleControllersFactory().init()
        for c in controllers:
            if isinstance(c, TeamChannelController):
                self._controllers['team'] = c
            elif isinstance(c, CommonChannelController):
                self._controllers['common'] = c
            elif isinstance(c, SquadChannelController):
                self._controllers['squad'] = c
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
        if not self.has_channel(channel) or not text:
            log.info('channel not found: "{}"'.format(channel))
            return False
        delay = self._textDelay
        self._setCallback(delay, partial(self._controllers[channel]._broadcast, text))
        return True

    def sendTeam(self, text):
        return self.sendText('team', text)

    def sendSquad(self, text):
        return self.sendText('squad', text)

    def has_channel(self, channel):
        return self._controllers.has_key(channel)

    def getKeys(self):
        return self._controllers.keys()

