# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU

import math

import BigWorld
from gui.Scaleform.Battle import Battle
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from ModUtils import BattleUtils,MinimapUtils,FileUtils,HotKeysUtils,DecorateUtils
from IngameMessanger import IngameMessanger
import const
import log

class SpotMessanger(object):
    _isEnabled = True
    _lastActivity = 0

    def setConfig(self, settings):
        self._settings = settings
    
    def initialize(self):
        self._isEnabled = self._settings['ActiveByDefault']
        self._lastActivity = 0
        self.showCurrentMode()

    def toggleActive(self):
        self._isEnabled = not self._isEnabled
        self.showCurrentMode()

    def showCurrentMode(self):
        if self._isEnabled:
            log.debug('Sixth Sense Message enabled')
            BattleUtils.DebugMsg(self._settings['EnableSystemMsg'], True)
        else:
            log.debug('Sixth Sense Message disabled')
            BattleUtils.DebugMsg(self._settings['DisableSystemMsg'], True)

    def _isCooldown(self, currentTime):
        cooldownTime = self._lastActivity + self._settings['CooldownInterval'] - currentTime
        if cooldownTime > 0:
            log.debug('[time:{:.1f}] activate sixth sense, but it\'s not time yet. (rest {:.1f}s)'.format(currentTime, cooldownTime))
            BattleUtils.DebugMsg(self._settings['CooldownMsg'].format(rest=int(math.ceil(cooldownTime))))
            return True
        return False

    def showSixthSenseIndicator(self):
        if not self._isEnabled:
            return

        currentTime = BigWorld.time()
        if self._isCooldown(currentTime):
            return
        self._lastActivity = currentTime
        log.debug('[time:{:.1f}] activate sixth sense, do commands.'.format(currentTime))
 
        player = BattleUtils.getPlayer()
        battleTypeName = _getBattleTypeName(player)
        vehicleTypeName = _getVehicleTypeName(player)

        teamAmount = BattleUtils.getTeamAmount(player)
        position = MinimapUtils.getOwnPos(player)

        messenger = IngameMessanger(self._settings)
        for channelType in [ 'team', 'squad' ]:
            if messenger.has_channel(channelType):
                log.debug('channel "{}" found.'.format(channelType))
	
        param = self._settings.get(battleTypeName, None)
        if not param:
            log.debug('setting for battle type "{}" is none, use default'.format(battleTypeName))
            param = self._settings.get('default')

        # vehicle type checks
        if not param['VehicleTypes'].get(vehicleTypeName, True):
            log.debug('Vehicle type "{}" is disabled.'.format(vehicleTypeName))
            return

        #team amount checks
        maxTeamAmount = param.get('MaxTeamAmount', 0)
        log.debug('team amount "{}"'.format(teamAmount))
        if maxTeamAmount > 0 and maxTeamAmount < teamAmount:
            log.debug('team amount "{}" is greater than "{}", do nothing.'.format(teamAmount, maxTeamAmount))
            return

        msg = self._settings.get('ImSpotted', None)
        
        for c in param['Order']:
            if c == 'ping':
                log.info('action: "{}", do ping at {}'.format(c, position))
                messenger.doPing(MinimapUtils.name2cell(position))
            elif c == 'help':
                log.info('action: "{}", call help'.format(c))
                messenger.callHelp()
            elif c == 'teammsg' and msg and msg != 'None':
                log.info('action: "{}", send message with team channel'.format(c))
                messenger.sendText('team', msg.format(pos=position))
            elif c == 'squadmsg' and msg and msg != 'None':
                log.info('action: "{}", send message with squad channel'.format(c))
                if messenger.has_channel('squad'):
                    messanger.sendText('squad', msg.format(pos=position))
                else:
                    log.info('action: "{}", no squad channel found.'.format(c))


def _getBattleTypeName(player):
    import constants
    type = player.arena.guiType
    name = const.BATTLE_TYPE.LABELS.get(type, 'Unknown')
    log.debug('battle type: "{}" (official: {}:{})'.format(name, type, constants.ARENA_GUI_TYPE_LABEL.LABELS[type]))
    return name

def _getVehicleTypeName(player):
    type = BattleUtils.getVehicleType(BattleUtils.getCurrentVehicleDesc(player))
    name = const.VEHICLE_TYPE.LABELS[type]
    log.debug('vehicle type: "{}"'.format(name))
    return name	


sm_control = SpotMessanger()
