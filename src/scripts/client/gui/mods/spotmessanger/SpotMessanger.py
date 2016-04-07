# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU, Chirimen SEA

import math

from modconsts import COMMAND_TYPE
from ModUtils import BattleUtils, MinimapUtils
from wotapis import Utils, VehicleInfo, ArenaInfo
from IngameMessanger import IngameMessanger
from logger import log

_commandMethod = {
    COMMAND_TYPE.LABELS.PING: '_doPing',
    COMMAND_TYPE.LABELS.HELP: '_doHelp',
    COMMAND_TYPE.LABELS.TEAMMSG: '_doSendTeamMsg',
    COMMAND_TYPE.LABELS.SQUADMSG: '_doSendSquadMsg'
}

class SpotMessanger(object):
    _isEnabled = True
    _lastActivity = 0
    _currentParam = {}

    def setConfig(self, settings):
        self._settings = settings
    
    def getFallbackParam(self, key):
        value = self._currentParam.get(key, None)
        if not value:
            value = self._settings.get(key, None)
        return value

    def initialize(self):
        self._isEnabled = self._settings['ActiveByDefault']
        self._lastActivity = 0

        player = Utils.getPlayer()
        arena = ArenaInfo(player=player)
        vehicle = VehicleInfo(player=player)
        log.debug('Vehicle Class: {} [{}] ({})'.format(vehicle.classAbbr, vehicle.className, vehicle.name))
        
        self._currentParam = self._settings['BattleType'].get(arena.battleType, None)
        if not self._currentParam:
            log.debug('setting for battle type "{}" is none, use default'.format(arena.battleType))
            self._currentParam = self._settings['BattleType'].get('default')

        self._cooldownInterval = self.getFallbackParam('CooldownInterval')
        self._commandDelay = self.getFallbackParam('CommandDelay')
        self._textDelay = self.getFallbackParam('TextDelay')

        self._isEnabledVehicle = vehicle.classAbbr in self._currentParam['EnableVehicleType']
        
        self.showCurrentMode()
        log.info('Battle Type: {} [{}({}) = "{}"]'.format(arena.battleType, arena.attrLabel, arena.id, arena.name))
        log.info('CooldownInterval: {}, CommandDelay: {}, TextDelay: {}'.format(self._cooldownInterval, self._commandDelay, self._textDelay))
        log.info('Command Order: {}'.format(self._currentParam.get('CommandOrder', [])))
        log.info('Max Team Amount: {}'.format(self._currentParam.get('MaxTeamAmount')))
        log.info('Enable Vehicle Type: {}'.format(self._currentParam.get('EnableVehicleType')))
        if self._isEnabledVehicle:
            log.info('current vehicle type is {}, sixth sense message is enabled.'.format(vehicle.classAbbr))
        else:
            log.info('current vehicle type is {}, sixth sense message is disabled.'.format(vehicle.classAbbr))


    def toggleActive(self):
        self._isEnabled = not self._isEnabled
        self.showCurrentMode()

    def showCurrentMode(self):
        if self._isEnabled:
            log.info('Sixth Sense Message enabled')
            BattleUtils.DebugMsg(self._settings['EnableSystemMsg'], True)
        else:
            log.info('Sixth Sense Message disabled')
            BattleUtils.DebugMsg(self._settings['DisableSystemMsg'], True)

    def _isCooldown(self, currentTime):
        cooldownTime = self._lastActivity + self._cooldownInterval - currentTime
        return cooldownTime > 0

    def showSixthSenseIndicator(self):
        if not self._isEnabled or not self._isEnabledVehicle:
            return

        currentTime = Utils.getTime()
        if self._isCooldown(currentTime):
            log.info('[time:{:.1f}] activate sixth sense, but it\'s not time yet. (rest {:.1f}s)'.format(currentTime, cooldownTime))
            BattleUtils.DebugMsg(self._settings['CooldownMsg'].format(rest=int(math.ceil(cooldownTime))))
            return
        log.debug('[time:{:.1f}] activate sixth sense, do commands.'.format(currentTime))

        player = Utils.getPlayer()
        teamAmount = BattleUtils.getTeamAmount(player)
        position = MinimapUtils.getOwnPos(player)

        messenger = IngameMessanger(commandDelay=self._commandDelay, textDelay=self._textDelay)
        log.debug('channel found: {}'.format(', '.join(messenger.getKeys())))

        #team amount checks
        maxTeamAmount = self._currentParam.get('MaxTeamAmount', 0)
        if maxTeamAmount > 0 and maxTeamAmount < teamAmount:
            log.debug('current team amount "{}" is greater than "{}", do nothing.'.format(teamAmount, maxTeamAmount))
            return
        log.debug('current team amount "{}"'.format(teamAmount))

        log.info('command order: {}'.format(self._currentParam.get('CommandOrder', [])))
        for command in self._currentParam.get('CommandOrder', []):
            if getattr(self, _commandMethod[command])(messenger, pos=position):
                self._lastActivity = currentTime


    def _doPing(self, messenger, pos=None):
        if not pos:
            return False
        log.info('action: do ping at {}'.format(pos))
        messenger.doPing(MinimapUtils.name2cell(pos))
        return True
        
    def _doHelp(self, messenger):
        log.info('action: call help')
        messenger.callHelp()
        return True

    def _doSendTeamMsg(self, messenger, pos=None):
        msg = self._settings.get('ImSpotted', '').format(pos=pos)
        if not msg:
            return False
        log.info('action: send message to team channel: "{}"'.format(msg))
        return messenger.sendTeam(msg)
        
    def _doSendSquadMsg(self, messenger, pos=None):
        msg = self._settings.get('ImSpotted', '').format(pos=pos)
        if not msg:
            return False
        log.info('action: send message to squad channel: "{}"'.format(msg))
        return messenger.sendSquad(msg)


sm_control = SpotMessanger()
