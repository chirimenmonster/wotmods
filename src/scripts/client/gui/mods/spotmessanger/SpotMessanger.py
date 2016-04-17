# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU, Chirimen SEA

import math

from modconsts import COMMAND_TYPE
from ModUtils import BattleUtils, MinimapUtils
from wotapis import Utils, VehicleInfo, ArenaInfo
from IngameMessanger import IngameMessanger
from settings import sm_settings
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
    
    def onBattleStart(self):
        self._isEnabled = sm_settings.get('ActiveByDefault')
        self._lastActivity = 0

        arena = ArenaInfo()
        vehicle = VehicleInfo()
        log.debug('Vehicle Class: {} [{}] ({})'.format(vehicle.classAbbr, vehicle.className, vehicle.name))
        
        sm_settings.setBattleType(arena.battleType)
 
        self._cooldownInterval = sm_settings.get('CooldownInterval')
        self._commandDelay = sm_settings.get('CommandDelay')
        self._textDelay = sm_settings.get('TextDelay')

        self._isEnabledVehicle = vehicle.classAbbr in sm_settings.get('EnableVehicleType')
        
        self.showCurrentMode()
        log.info('Battle Type: {} [{}({}) = "{}"]'.format(arena.battleType, arena.attrLabel, arena.id, arena.name))
        log.info('CooldownInterval: {}, CommandDelay: {}, TextDelay: {}'.format(self._cooldownInterval, self._commandDelay, self._textDelay))
        log.info('Command Order: {}'.format(sm_settings.get('CommandOrder', [])))
        log.info('Max Team Amount: {}'.format(sm_settings.get('MaxTeamAmount')))
        log.info('Enable Vehicle Type: {}'.format(sm_settings.get('EnableVehicleType')))
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
            BattleUtils.DebugMsg(sm_settings.get('EnableSystemMsg'), True)
        else:
            log.info('Sixth Sense Message disabled')
            BattleUtils.DebugMsg(sm_settings.get('DisableSystemMsg'), True)

    def _getCooldownTime(self, currentTime):
        cooldownTime = self._lastActivity + self._cooldownInterval - currentTime
        return cooldownTime if cooldownTime > 0 else 0

    def showSixthSenseIndicator(self):
        if not self._isEnabled or not self._isEnabledVehicle:
            return

        currentTime = Utils.getTime()
        cooldownTime = self._getCooldownTime(currentTime)
        if cooldownTime > 0:
            log.info('[time:{:.1f}] activate sixth sense, but it\'s not time yet. (rest {:.1f}s)'.format(currentTime, cooldownTime))
            BattleUtils.DebugMsg(sm_settings.get('CooldownMsg').format(rest=int(math.ceil(cooldownTime))))
            return
        log.debug('[time:{:.1f}] activate sixth sense, do commands.'.format(currentTime))

        player = Utils.getPlayer()
        teamAmount = BattleUtils.getTeamAmount(player)
        position = MinimapUtils.getOwnPos(player)

        messenger = IngameMessanger(commandDelay=self._commandDelay, textDelay=self._textDelay)
        log.debug('channel found: {}'.format(', '.join(messenger.getChannelLabels())))

        #team amount checks
        maxTeamAmount = self._currentParam.get('MaxTeamAmount', 0)
        if maxTeamAmount > 0 and maxTeamAmount < teamAmount:
            log.debug('current team amount "{}" is greater than "{}", do nothing.'.format(teamAmount, maxTeamAmount))
            return
        log.debug('current team amount "{}"'.format(teamAmount))

        log.info('command order: {}'.format(sm_settings.get('CommandOrder', [])))
        for command in sm_settings.get('CommandOrder', []):
            if getattr(self, _commandMethod[command])(messenger, pos=position):
                self._lastActivity = currentTime


    def _doPing(self, messenger, pos=None):
        if not pos:
            return False
        log.info('action: do ping at {}'.format(pos))
        messenger.doPing(MinimapUtils.name2cell(pos))
        return True
        
    def _doHelp(self, messenger, pos=None):
        log.info('action: call help')
        messenger.callHelp()
        return True

    def _doSendTeamMsg(self, messenger, pos=None):
        msg = sm_settings.get('ImSpotted', '').format(pos=pos)
        if not msg:
            return False
        log.info('action: send message to team channel: "{}"'.format(msg))
        return messenger.sendTeam(msg)
        
    def _doSendSquadMsg(self, messenger, pos=None):
        msg = sm_settings.get('ImSpotted', '').format(pos=pos)
        if not msg:
            return False
        log.info('action: send message to squad channel: "{}"'.format(msg))
        return messenger.sendSquad(msg)


sm_control = SpotMessanger()
