# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU
import BigWorld
from messenger.gui.Scaleform.channels.bw_chat2.factories import BattleControllersFactory
from messenger.gui.Scaleform.channels.bw_chat2.battle_controllers import TeamChannelController, CommonChannelController, SquadChannelController
from chat_shared import CHAT_COMMANDS
from functools import partial
import log

class IngameMessanger(object):
    myConf = {"TextDelay":0.5,"CommandDelay":5}
    _cooldDown = 0

    @staticmethod
    def getChannelControllers():
        dict = {}
        controllers = BattleControllersFactory().init()
        for controller in controllers:
            if isinstance(controller, TeamChannelController):
                dict['team'] = controller
            elif isinstance(controller, CommonChannelController):
                dict['common'] = controller
            elif isinstance(controller, SquadChannelController):
                dict['squad'] = controller
            else:
                log.warning('unknwon channel controller')
        return dict
		
    @staticmethod
    def getCommandfactory():
        from gui.battle_control import g_sessionProvider
        cmdFc = g_sessionProvider.getChatCommands().proto.battleCmd
        if cmdFc is None:
            log.error('Commands factory is not defined')
        return cmdFc              
    
    @staticmethod
    def doPing(controller, cellIdx):  
        command = IngameMessanger.getCommandfactory().createByCellIdx(cellIdx)
        IngameMessanger.sendCommand(controller, command) 

    @staticmethod
    def callHelp(controller):
        command = IngameMessanger.getCommandfactory().createByName(CHAT_COMMANDS.HELPME.name())
        IngameMessanger.sendCommand(controller, command)

    @staticmethod
    def sendCommand(controller, command):
        diff = IngameMessanger._cooldDown - BigWorld.time()
        if diff < 0:
            diff = 0
            IngameMessanger._cooldDown = BigWorld.time()
        IngameMessanger._cooldDown += IngameMessanger.myConf['CommandDelay']
        BigWorld.callback(diff, partial(controller.sendCommand, command))

    @staticmethod
    def sendText(controller, text):
        diff = IngameMessanger._cooldDown - BigWorld.time()
        if diff < 0:
            diff = 0
            IngameMessanger._cooldDown = BigWorld.time()
        IngameMessanger._cooldDown += IngameMessanger.myConf['TextDelay']
        BigWorld.callback(diff, partial(controller._broadcast, text))

