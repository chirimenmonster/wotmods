# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU, Chirimen SEA

import math

from modconsts import COMMAND_TYPE, VEHICLE_TYPE
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

        log.info('on battle start')
        log.info('current battle type: {} [{}({}) = "{}"]'.format(arena.battleType, arena.attrLabel, arena.id, arena.name))
        log.info('current vehicle class: {} [{}] ({})'.format(vehicle.classAbbr, vehicle.className, vehicle.name))

        self._currentParams = []
        cooldownInterval = []
        count = 0
        for p in sm_settings.getParamsBattleType(arena.battleType):
            log.info('[{}]: Command Order: {}'.format(count, p.get('CommandOrder', [])))
            log.info('[{}]: CooldownInterval: {}, CommandDelay: {}, TextDelay: {}'.format(count,
                    p.get('CooldownInterval', 'inherit ({})'.format(sm_settings.get('CooldownInterval'))),
                    p.get('CommandDelay', 'inherit ({})'.format(sm_settings.get('CommandDelay'))),
                    p.get('TextDelay', 'inherit ({})'.format(sm_settings.get('TextDelay')))))
            log.info('[{}]: MinTeamAmount: {}, MaxTeamAmount: {}'.format(count,
                    p.get('MinTeamAmount', 'inherit ({})'.format(sm_settings.get('MinTeamAmount'))),
                    p.get('MaxTeamAmount', 'inherit ({})'.format(sm_settings.get('MaxTeamAmount') or 'undef'))))
            log.info('[{}]: Enable Vehicle Type: {}'.format(count, p.get('EnableVehicleType', 'undef')))
            if vehicle.classAbbr in p.get('EnableVehicleType', VEHICLE_TYPE.LIST):
                log.info('[{}]: current vehicle type is {}, add to list.'.format(count, vehicle.classAbbr))
                self._currentParams.append(p)
                cooldownInterval.append(p.get('CooldownInterval', sm_settings.get('CooldownInterval')))
            else:
                log.info('[{}]: current vehicle type is {}, do nothing.'.format(count, vehicle.classAbbr))
                self._currentParams.append(None)
            count += 1

        self._cooldownInterval = min(t for t in cooldownInterval)
        log.info('minimal CoolDownInterval: {}'.format(self._cooldownInterval))
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
            log.info('sixth sense message is disabled or nothing to do.')
            return
        currentTime = Utils.getTime()
        cooldownTime = self._getCooldownTime(currentTime, self._cooldownInterval)
        if cooldownTime > 0:
            log.info('[time:{:.1f}] invoke sixth sense, but it\'s not time yet. (rest {:.1f}s)'.format(currentTime, cooldownTime))
            BattleUtils.DebugMsg(sm_settings.get('CooldownMsg').format(rest=int(math.ceil(cooldownTime))))
            return
        log.info('[time:{:.1f}] invoke sixth sense.'.format(currentTime))

        player = Utils.getPlayer()
        teamAmount = BattleUtils.getTeamAmount(player)
        position = MinimapUtils.getOwnPos(player)
        
        messenger = IngameMessanger()
        log.info('current chat channel: {}'.format(', '.join(messenger.getChannelLabels())))
        log.info('current team amount: {}'.format(teamAmount))

        self._isDone = {}
        for index, param in enumerate(self._currentParams):
            self._doSixthSense(index, param, messenger, currentTime, player, position, teamAmount)
        if self._isDone:
            log.debug('success commands, update last activity.')
            self._lastActivity = currentTime


    def _doSixthSense(self, index, param, messenger, currentTime, player, position, teamAmount):
        cooldownInterval = param.get('CooldownInterval', sm_settings.get('CooldownInterval'))
        commandDelay = param.get('CommandDelay', sm_settings.get('CommandDelay'))
        textDelay = param.get('TextDelay', sm_settings.get('TextDelay'))
        minTeamAmount = param.get('MinTeamAmount', sm_settings.get('MinTeamAmount'))
        maxTeamAmount = param.get('MaxTeamAmount', sm_settings.get('MaxTeamAmount'))
 
        cooldownTime = self._getCooldownTime(currentTime, cooldownInterval)
        if cooldownTime > 0:
            log.info('[{}]: now cooldown time, skip. (rest {:.1f}s)'.format(index, cooldownTime))
            return

        messenger.setParam(commandDelay, textDelay)

        if minTeamAmount and teamAmount <= minTeamAmount:
            log.info('[{}]: team amount ({}) is too less (<= {}), skip.'.format(index, teamAmount, minTeamAmount))
            return
        if maxTeamAmount and teamAmount > maxTeamAmount:
            log.info('[{}]: team amount ({}) is too many (> {}), skip.'.format(index, teamAmount, maxTeamAmount))
            return

        commandOrder = param.get('CommandOrder', [])
        log.info('[{}]: command order: {}'.format(index, commandOrder))
        for command in commandOrder:
            log.debug('[{}]: already executed command class: {}'.format(index, self._isDone))
            getattr(self, _commandMethod[command])(messenger, pos=position)


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
        if not 'squad' in messenger.getChannelLabels():
            log.info('action: no squad channel, skip.')
            return
        log.info('action: send message to squad channel: "{}"'.format(msg))
        ret = messenger.sendSquad(msg)
        self._isDone['msg'] = ret
        return ret


sm_control = SpotMessanger()
