# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU, Chirimen SEA

import math

from version import MOD_INFO
from modconsts import COMMAND_TYPE, VEHICLE_TYPE
from wotapi import sysutils, avatarutils, chatutils, minimaputils
from delaychat import DelayChatControl
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
    _activeParams = []
    _currentIndex = 0
    _currentParam = None

    def __init__(self, settings):
        self.settings = settings
        
    def onBattleStart(self):
        self._isEnabled = self.settings.get('ActiveByDefault')
        self._lastActivity = 0
        self._isObserver = avatarutils.isObserver()

        guiType = avatarutils.getArenaGuiTypeInfo()
        arenaType = avatarutils.getArenaTypeInfo()
        vehicle = avatarutils.getVehicleInfo()

        log.info('on battle start')
        if self._isObserver:
            log.info('player avatar is observer, nothing to do')
            return
        log.info('current battle type: {} [{}({}) = "{}"], "{}" ({})'.format(
            guiType.battleType, guiType.attrLabel, guiType.id, guiType.name,
            arenaType.name, arenaType.geometryName))
        log.info('current vehicle class: {} [{}] ({})'.format(vehicle.classAbbr, vehicle.className, vehicle.name))

        self._activeParams = []
        cooldownInterval = []
        for i, p in enumerate(self.settings.getParamsBattleType(guiType.battleType)):
            log.info('[{}]: CommandOrder: {}'.format(i, p.getInfo('CommandOrder')))
            log.info('[{}]: CooldownInterval: {}, CommandDelay: {}, TextDelay: {}'.format(i,
                    p.getInfo('CooldownInterval'),
                    p.getInfo('CommandDelay'),
                    p.getInfo('TextDelay')))
            log.info('[{}]: MinTeamAmount: {}, MaxTeamAmount: {}'.format(i,
                    p.getInfo('MinTeamAmount'),
                    p.getInfo('MaxTeamAmount')))
            log.info('[{}]: Enable Vehicle Type: {}'.format(i, p.getInfo('EnableVehicleType')))
            if vehicle.classAbbr in p.get('EnableVehicleType', VEHICLE_TYPE.LIST):
                log.info('[{}]: current vehicle type is {}, add to list.'.format(i, vehicle.classAbbr))
                self._activeParams.append(p)
                cooldownInterval.append(p.get('CooldownInterval'))
            else:
                log.info('[{}]: current vehicle type is {}, do nothing.'.format(i, vehicle.classAbbr))
                self._activeParams.append(None)

        self._cooldownInterval = min(t for t in cooldownInterval)
        log.info('minimal CoolDownInterval: {}'.format(self._cooldownInterval))
        self.showCurrentMode()

    def reloadConfig(self, conf_file, conf_prefix):
        self.settings.readConfig(conf_file, conf_prefix)
        self.addSystemMessage('{}: reload config file'.format(MOD_INFO.NAME))

    def addSystemMessage(self, message):
        if self.settings.get('NotifyCenter'):
            sysutils.addSystemMessage(message)    
        
    def toggleActive(self):
        self._isEnabled = not self._isEnabled
        self.showCurrentMode()

    def showCurrentMode(self):
        if self._isEnabled:
            log.info('Sixth Sense Message enabled')
            msg = self.settings.get('EnableSystemMsg')
        else:
            log.info('Sixth Sense Message disabled')
            msg = self.settings.get('DisableSystemMsg')    
        if avatarutils.getArena():
            chatutils.addClientMessage(msg)
        else:
            self.addSystemMessage(msg)

    def _getCooldownTime(self, currentTime, cooldownInterval):
        cooldownTime = self._lastActivity + cooldownInterval - currentTime
        return cooldownTime if cooldownTime > 0 else 0

    def showSixthSenseIndicator(self):
        if self._isObserver:
            return
        if avatarutils.isPostMortem():
            log.info('current control mode is postmortem, nothing to do.')
            return
        if not self._isEnabled or not self._activeParams:
            log.info('sixth sense message is disabled or nothing to do.')
            return
        currentTime = sysutils.getTime()
        cooldownTime = self._getCooldownTime(currentTime, self._cooldownInterval)
        if cooldownTime > 0:
            log.info('[time:{:.1f}] invoke sixth sense, but it\'s not time yet. (rest {:.1f}s)'.format(currentTime, cooldownTime))
            chatutils.addClientMessage(self.settings.get('CooldownMsg').format(rest=int(math.ceil(cooldownTime))))
            return
        log.info('[time:{:.1f}] invoke sixth sense.'.format(currentTime))

        player = avatarutils.getPlayer()
        teamAmount = avatarutils.getTeamAmount()
        cellIndex = minimaputils.getCellIndexByPosition(avatarutils.getPos())
        
        messenger = DelayChatControl()
        log.info('current chat channel: {}'.format(chatutils.getChannelLabels()))
        log.info('current team amount: {}'.format(teamAmount))

        self._isDone = {}
        for index, param in enumerate(self._activeParams):
            self._currentIndex = index
            self._currentParam = param
            self._doSixthSense(messenger, currentTime, player, cellIndex, teamAmount)
        if self._isDone:
            log.debug('success commands, update last activity.')
            self._lastActivity = currentTime

    def _doSixthSense(self, messenger, currentTime, player, cellIndex, teamAmount):
        index = self._currentIndex
        param = self._currentParam
        cooldownInterval = param.get('CooldownInterval')
        commandDelay = param.get('CommandDelay')
        textDelay = param.get('TextDelay')
        minTeamAmount = param.get('MinTeamAmount')
        maxTeamAmount = param.get('MaxTeamAmount')
 
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
            getattr(self, _commandMethod[command])(messenger, cellIndex=cellIndex)

    def _doPing(self, messenger, cellIndex=None):
        if self._isDone.get('ping') or not cellIndex:
            return
        log.info('[{}]: action: do ping at {}'.format(self._currentIndex, minimaputils.getCellName(cellIndex)))
        self._isDone['ping'] = messenger.doPing(cellIndex)

    def _doHelp(self, messenger, cellIndex=None):
        if self._isDone.get('help'):
            return
        log.info('[{}]: action: call help'.format(self._currentIndex))
        self._isDone['help'] = messenger.callHelp()

    def _doSendTeamMsg(self, messenger, cellIndex=None):
        if self._isDone.get('msg'):
            return
        msg = self._currentParam.get('ImSpotted').format(pos=minimaputils.getCellName(cellIndex))
        if not msg:
            return
        log.info('[{}]: action: send message to team channel: "{}"'.format(self._currentIndex, msg))
        self._isDone['msg'] = messenger.sendTeam(msg)

    def _doSendSquadMsg(self, messenger, cellIndex=None):
        if self._isDone.get('msg'):
            return
        msg = self._currentParam.get('ImSpotted').format(pos=minimaputils.getCellName(cellIndex))
        if not msg:
            return
        if not chatutils.isExistSquadChannel():
            log.info('[{}]: action: no squad channel, skip.'.format(self._currentIndex))
            return
        log.info('[{}]: action: send message to squad channel: "{}"'.format(self._currentIndex, msg))
        self._isDone['msg'] = messenger.sendSquad(msg)
