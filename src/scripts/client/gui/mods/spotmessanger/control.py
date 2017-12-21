# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU, Chirimen SEA

import math

from version import MOD_INFO
from modconsts import COMMAND_TYPE, VEHICLE_TYPE
from wotapi import sysutils, avatarutils, chatutils, minimaputils
from delaychat import DelayChatControl
from logger import log


class SpotMessanger(object):
    _isEnabled = True
    _lastActivity = 0
    _activeParams = []

    def __init__(self, settings):
        self.settings = settings
        self._commandMethod = {
            COMMAND_TYPE.LABELS.PING: self._doPing,
            COMMAND_TYPE.LABELS.HELP: self._doHelp,
            COMMAND_TYPE.LABELS.TEAMMSG: self._doSendTeamMsg,
            COMMAND_TYPE.LABELS.SQUADMSG: self._doSendSquadMsg
        }

    def onBattleStart(self):
        self._isEnabled = self.settings['ActiveByDefault']
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
        for p in self.settings.getParamsBattleType(guiType.battleType):
            i = p['index']
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
                cooldownInterval.append(p['CooldownInterval'])
            else:
                log.info('[{}]: current vehicle type is {}, ignore.'.format(i, vehicle.classAbbr))
        if not self._activeParams:
            log.info('nothing to do for current battle type and vehicle class')
            return
            
        self._cooldownInterval = min(t for t in cooldownInterval)
        log.info('minimal CoolDownInterval: {}'.format(self._cooldownInterval))
        self.showCurrentMode()

    def reloadConfig(self, conf_file, conf_prefix):
        self.settings.readConfig(conf_file, conf_prefix)
        self.addSystemMessage('{}: reload config file'.format(MOD_INFO.NAME))

    def addSystemMessage(self, message):
        if self.settings['NotifyCenter']:
            sysutils.addSystemMessage(message)    
        
    def toggleActive(self):
        self._isEnabled = not self._isEnabled
        self.showCurrentMode()

    def showCurrentMode(self):
        if self._isEnabled:
            log.info('Sixth Sense Message enabled')
            msg = self.settings['EnableSystemMsg']
        else:
            log.info('Sixth Sense Message disabled')
            msg = self.settings['DisableSystemMsg']    
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
        log.info('current control mode: \'{}\''.format(avatarutils.getCtrlModeName()))
        if not avatarutils.isValidCtrlMode():
            log.info('current control mode is not valid, ignore.')
            return
        if not self._isEnabled or not self._activeParams:
            log.info('sixth sense message is disabled or nothing to do.')
            return
        currentTime = sysutils.getTime()
        cooldownTime = self._getCooldownTime(currentTime, self._cooldownInterval)
        if cooldownTime > 0:
            log.info('[time:{:.1f}] invoke sixth sense, but it\'s not time yet. (rest {:.1f}s)'.format(currentTime, cooldownTime))
            chatutils.addClientMessage(self.settings['CooldownMsg'].format(rest=int(math.ceil(cooldownTime))))
            return
        log.info('[time:{:.1f}] invoke sixth sense.'.format(currentTime))

        teamAmount = avatarutils.getTeamAmount()
        squadAmount = avatarutils.getSquadAmount()
        cellIndex = minimaputils.getCellIndexByPosition(avatarutils.getPos())
        
        messenger = DelayChatControl()
        log.info('current chat channel: {}'.format(chatutils.getChannelLabels()))
        log.info('current ally amount w/o myself: (team, squad) = ({}, {})'.format(teamAmount, squadAmount))

        self._isDone = { 'ping': False, 'help': False, 'msg': False }
        for param in self._activeParams:
            self._doSixthSense(param, messenger, currentTime, cellIndex, teamAmount, squadAmount)
        if self._isDone.values().count(True):
            log.debug('success commands, update last activity.')
            self._lastActivity = currentTime

    def _doSixthSense(self, param, messenger, currentTime, cellIndex, teamAmount, squadAmount):
        index = param['index']
        cooldownTime = self._getCooldownTime(currentTime, param['CooldownInterval'])
        if cooldownTime > 0:
            log.info('[{}]: now cooldown time, skip. (rest {:.1f}s)'.format(index, cooldownTime))
            return

        minTeamAmount = param['MinTeamAmount']
        maxTeamAmount = param['MaxTeamAmount']
        if minTeamAmount and teamAmount < minTeamAmount:
            log.info('[{}]: team amount ({}) is too less (< {}), skip.'.format(index, teamAmount, minTeamAmount))
            return
        if maxTeamAmount and teamAmount > maxTeamAmount:
            log.info('[{}]: team amount ({}) is too many (> {}), skip.'.format(index, teamAmount, maxTeamAmount))
            return

        messenger.setParam(param['CommandDelay'], param['TextDelay'])
        commandOrder = param.get('CommandOrder', [])
        log.info('[{}]: command order: {}'.format(index, commandOrder))
        for command in commandOrder:
            self._commandMethod[command](param, messenger, cellIndex=cellIndex, squadAmount=squadAmount)

    def _doPing(self, param, messenger, cellIndex, **kwargs):
        if self._isDone['ping']:
            log.info('[{}][ping]: action: "ping" is already executed'.format(param['index']))
            return
        log.info('[{}][ping]: action: do ping at {}'.format(param['index'], minimaputils.getCellName(cellIndex)))
        self._isDone['ping'] = messenger.doPing(cellIndex)

    def _doHelp(self, param, messenger, **kwargs):
        if self._isDone['help']:
            log.info('[{}][help]: action: "help" is already executed'.format(param['index']))
            return
        log.info('[{}][help]: action: call help'.format(param['index']))
        self._isDone['help'] = messenger.callHelp()

    def _doSendTeamMsg(self, param, messenger, cellIndex, **kwargs):
        if self._isDone['msg']:
            log.info('[{}][teammsg]: action: "send message" is already executed'.format(param['index']))
            return
        msg = param['ImSpotted'].format(pos=minimaputils.getCellName(cellIndex))
        if not msg:
            return
        log.info('[{}][teammsg]: action: send message to team channel: "{}"'.format(param['index'], msg))
        self._isDone['msg'] = messenger.sendTeam(msg)

    def _doSendSquadMsg(self, param, messenger, cellIndex, squadAmount, **kwargs):
        if self._isDone['msg']:
            log.info('[{}][squadmsg]: action: "send message" is already executed'.format(param['index']))
            return
        msg = param['ImSpotted'].format(pos=minimaputils.getCellName(cellIndex))
        if not msg:
            return
        if not chatutils.isExistSquadChannel():
            log.info('[{}][squadmsg]: action: no squad channel, skip.'.format(param['index']))
            return
        if squadAmount == 0 and param['MinTeamAmount'] != 0:
            log.info('[{}][squadmsg]: action: squad amount = 0, skip.'.format(param['index'], squadAmount))
            return
        log.info('[{}][squadmsg]: action: send message to squad channel: "{}"'.format(param['index'], msg))
        self._isDone['msg'] = messenger.sendSquad(msg)
