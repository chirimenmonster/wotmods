# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU, Chirimen SEA

import math

from ModUtils import BattleUtils, MinimapUtils
from IngameMessanger import IngameMessanger
from logger import log

from wotapis import VehicleInfo, ArenaInfo, getBattleTime

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
        self._player = BattleUtils.getPlayer()

        arena = ArenaInfo(player=self._player)

        vehicle = VehicleInfo(self._player.playerVehicleID)
        vehicleType = vehicle.classAbbr
        log.debug('Vehicle Class: {} [{}] ({})'.format(vehicleType, vehicle.className, vehicle.name))
        
        self._currentParam = self._settings['BattleType'].get(arena.battleType, None)
        if not self._currentParam:
            log.debug('setting for battle type "{}" is none, use default'.format(arena.battleType))
            self._currentParam = self._settings['BattleType'].get('default')

        self._cooldownInterval = self.getFallbackParam('CooldownInterval')
        self._commandDelay = self.getFallbackParam('CommandDelay')
        self._textDelay = self.getFallbackParam('TextDelay')

        self._isEnabledVehicle = vehicleType in self._currentParam['EnableVehicleType']
        
        self.showCurrentMode()
        log.info('Battle Type: {} [{}({}) = "{}"]'.format(arena.battleType, arena.attrLabel, arena.id, arena.name))
        log.info('CooldownInterval: {}, CommandDelay: {}, TextDelay: {}'.format(self._cooldownInterval, self._commandDelay, self._textDelay))
        log.info('Command Order: {}'.format(self._currentParam.get('CommandOrder', [])))
        log.info('Max Team Amount: {}'.format(self._currentParam.get('MaxTeamAmount')))
        log.info('Enable Vehicle Type: {}'.format(self._currentParam.get('EnableVehicleType')))
        if self._isEnabledVehicle:
            log.info('current vehicle type is {}, sixth sense message is enabled.'.format(vehicleType))
        else:
            log.info('current vehicle type is {}, sixth sense message is disabled.'.format(vehicleType))


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
        if cooldownTime > 0:
            log.info('[time:{:.1f}] activate sixth sense, but it\'s not time yet. (rest {:.1f}s)'.format(currentTime, cooldownTime))
            BattleUtils.DebugMsg(self._settings['CooldownMsg'].format(rest=int(math.ceil(cooldownTime))))
            return True
        return False

    def showSixthSenseIndicator(self):
        if not self._isEnabled or not self._isEnabledVehicle:
            return

        currentTime = getBattleTime()
        if self._isCooldown(currentTime):
            return
        log.debug('[time:{:.1f}] activate sixth sense, do commands.'.format(currentTime))
 
        teamAmount = BattleUtils.getTeamAmount(self._player)
        position = MinimapUtils.getOwnPos(self._player)

        messenger = IngameMessanger(commandDelay=self._commandDelay, textDelay=self._textDelay)
        log.debug('channel found: {}'.format(', '.join(messenger.getKeys())))

        #team amount checks
        maxTeamAmount = self._currentParam.get('MaxTeamAmount', 0)
        if maxTeamAmount > 0 and maxTeamAmount < teamAmount:
            log.debug('current team amount "{}" is greater than "{}", do nothing.'.format(teamAmount, maxTeamAmount))
            return
        log.debug('current team amount "{}"'.format(teamAmount))

        msg = self._settings.get('ImSpotted', None)
        msg = msg.format(pos=position) if msg else None
        
        commandOrder = self._currentParam.get('CommandOrder', [])
        if not commandOrder:
            log.warning('CommandOrder is empty')
            return
        for command in commandOrder:
            if command == 'ping':
                log.info('action: "{}", do ping at {}'.format(command, position))
                self._lastActivity = currentTime
                messenger.doPing(MinimapUtils.name2cell(position))
            elif command == 'help':
                log.info('action: "{}", call help'.format(command))
                self._lastActivity = currentTime
                messenger.callHelp()
            elif command == 'teammsg' and msg and msg != 'None':
                log.info('action: "{}", send message with team channel: "{}"'.format(command, msg))
                self._lastActivity = currentTime
                messenger.sendText('team', msg)
            elif command == 'squadmsg' and msg and msg != 'None':
                log.info('action: "{}", send message with squad channel: "{}"'.format(command, msg))
                if messenger.has_channel('squad'):
                    self._lastActivity = currentTime
                    messenger.sendText('squad', msg)
                else:
                    log.info('action: "{}", no squad channel found.'.format(command))


sm_control = SpotMessanger()
