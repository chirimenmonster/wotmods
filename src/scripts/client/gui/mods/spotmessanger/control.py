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
    _currentIndex = 0
    _currentParam = None

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
            i = p.get('index')
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
        cellIndex = minimaputils.getCellIndexByPosition(avatarutils.getPos())
        
        messenger = DelayChatControl()
        log.info('current chat channel: {}'.format(chatutils.getChannelLabels()))
        log.info('current team amount: {}'.format(teamAmount))

        self._isDone = {}
        for param in self._activeParams:
            self._doSixthSense(param, messenger, currentTime, cellIndex, teamAmount)
        if self._isDone:
            log.debug('success commands, update last activity.')
            self._lastActivity = currentTime

    def _doSixthSense(self, param, messenger, currentTime, cellIndex, teamAmount):
        index = param.get('index')
        cooldownInterval = param['CooldownInterval']
        commandDelay = param['CommandDelay']
        textDelay = param['TextDelay']
        minTeamAmount = param['MinTeamAmount']
        maxTeamAmount = param['MaxTeamAmount']
 
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
            self._commandMethod[command](param, messenger, cellIndex)

    def _doPing(self, param, messenger, cellIndex):
        if self._isDone.get('ping'):
            log.info('[{}]: action: "ping" is already executed'.format(param['index']))
            return
        log.info('[{}]: action: do ping at {}'.format(param['index'], minimaputils.getCellName(cellIndex)))
        self._isDone['ping'] = messenger.doPing(cellIndex)

    def _doHelp(self, param, messenger, cellIndex):
        if self._isDone.get('help'):
            log.info('[{}]: action: "help" is already executed'.format(param['index']))
            return
        log.info('[{}]: action: call help'.format(param['index']))
        self._isDone['help'] = messenger.callHelp()

    def _doSendTeamMsg(self, param, messenger, cellIndex):
        if self._isDone.get('msg'):
            log.info('[{}]: action: "send message" is already executed'.format(param['index']))
            return
        msg = param['ImSpotted'].format(pos=minimaputils.getCellName(cellIndex))
        if not msg:
            return
        log.info('[{}]: action: send message to team channel: "{}"'.format(param['index'], msg))
        self._isDone['msg'] = messenger.sendTeam(msg)

    def _doSendSquadMsg(self, param, messenger, cellIndex):
        if self._isDone.get('msg'):
            log.info('[{}]: action: "send message" is already executed'.format(param['index']))
            return
        msg = param['ImSpotted'].format(pos=minimaputils.getCellName(cellIndex))
        if not msg:
            return
        if not chatutils.isExistSquadChannel():
            log.info('[{}]: action: no squad channel, skip.'.format(param['index']))
            return
        log.info('[{}]: action: send message to squad channel: "{}"'.format(param['index'], msg))
        self._isDone['msg'] = messenger.sendSquad(msg)
