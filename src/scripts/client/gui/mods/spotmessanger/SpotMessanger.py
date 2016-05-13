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
    _currentParams = []
    
    def onBattleStart(self):
        self._isEnabled = sm_settings.get('ActiveByDefault')
        self._lastActivity = 0

        arena = ArenaInfo()
        vehicle = VehicleInfo()

        log.info('Battle Type: {} [{}({}) = "{}"]'.format(arena.battleType, arena.attrLabel, arena.id, arena.name))
        log.info('Vehicle Class: {} [{}] ({})'.format(vehicle.classAbbr, vehicle.className, vehicle.name))

        self._currentParams = []
        for p in sm_settings.getParamsBattleType(arena.battleType):
            log.info('Command Order: {}'.format(p.get('CommandOrder', [])))
            log.info('CooldownInterval: {}, CommandDelay: {}, TextDelay: {}'.format(p['CooldownInterval'], p['CommandDelay'], p['TextDelay']))
            log.info('Max Team Amount: {}'.format(p.get('MaxTeamAmount')))
            log.info('Enable Vehicle Type: {}'.format(p.get('EnableVehicleType')))
            if vehicle.classAbbr in p.get('EnableVehicleType', []):
                log.info('current vehicle type is {}, add to list.'.format(vehicle.classAbbr))
                self._currentParams.append(p)
            else:
                log.info('current vehicle type is {}, do nothing.'.format(vehicle.classAbbr))

        self._cooldownInterval = min(p['CooldownInterval'] for p in self._currentParams)
        self.showCurrentMode()

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

    def _getCooldownTime(self, currentTime, cooldownInterval):
        cooldownTime = self._lastActivity + cooldownInterval - currentTime
        return cooldownTime if cooldownTime > 0 else 0

    def showSixthSenseIndicator(self):
        if not self._isEnabled or not self._currentParams:
            return
        currentTime = Utils.getTime()
        cooldownTime = self._getCooldownTime(currentTime, self._cooldownInterval)
        if cooldownTime > 0:
            log.info('[time:{:.1f}] activate sixth sense, but it\'s not time yet. (rest {:.1f}s)'.format(currentTime, cooldownTime))
            BattleUtils.DebugMsg(sm_settings.get('CooldownMsg').format(rest=int(math.ceil(cooldownTime))))
            return
        log.debug('[time:{:.1f}] activate sixth sense, do commands.'.format(currentTime))

        player = Utils.getPlayer()
        teamAmount = BattleUtils.getTeamAmount(player)
        position = MinimapUtils.getOwnPos(player)

        messenger = IngameMessanger()
        log.debug('channel found: {}'.format(', '.join(messenger.getChannelLabels())))

        self._isDone = {}
        for param in self._currentParams:
            self._doSixthSense(param, messenger, currentTime, player, position, teamAmount)
            
    def _doSixthSense(self, param, messenger, currentTime, player, position, teamAmount):
        cooldownTime = self._getCooldownTime(currentTime, param['CooldownInterval'])
        if cooldownTime > 0:
            log.info('[time:{:.1f}] activate sixth sense, but it\'s not time yet. (rest {:.1f}s)'.format(currentTime, cooldownTime))
            return

        messenger.setParam(param['CommandDelay'], param['TextDelay'])

        maxTeamAmount = param.get('MaxTeamAmount', 0)
        if maxTeamAmount > 0 and maxTeamAmount < teamAmount:
            log.debug('current team amount "{}" is greater than "{}", do nothing.'.format(teamAmount, maxTeamAmount))
            return
        log.debug('current team amount "{}"'.format(teamAmount))

        commandOrder = param.get('CommandOrder', [])
        log.info('command order: {}'.format(commandOrder))
        for command in commandOrder:
            log.debug('_isDone: {}'.format(self._isDone))
            if getattr(self, _commandMethod[command])(messenger, pos=position):
                self._lastActivity = currentTime

    def _doPing(self, messenger, pos=None):
        if self._isDone.get('ping')or not pos:
            return False
        log.info('action: do ping at {}'.format(pos))
        messenger.doPing(MinimapUtils.name2cell(pos))
        self._isDone['ping'] = True
        return True
        
    def _doHelp(self, messenger, pos=None):
        if self._isDone.get('help'):
            return False
        log.info('action: call help')
        messenger.callHelp()
        self._isDone['help'] = True
        return True

    def _doSendTeamMsg(self, messenger, pos=None):
        if self._isDone.get('msg'):
            return False
        msg = sm_settings.get('ImSpotted', '').format(pos=pos)
        if not msg:
            return False
        log.info('action: send message to team channel: "{}"'.format(msg))
        ret = messenger.sendTeam(msg)
        self._isDone['msg'] = ret
        return ret
        
    def _doSendSquadMsg(self, messenger, pos=None):
        if self._isDone.get('msg'):
            return False
        msg = sm_settings.get('ImSpotted', '').format(pos=pos)
        if not msg:
            return False
        log.info('action: send message to squad channel: "{}"'.format(msg))
        ret = messenger.sendSquad(msg)
        self._isDone['msg'] = ret
        return ret


sm_control = SpotMessanger()
