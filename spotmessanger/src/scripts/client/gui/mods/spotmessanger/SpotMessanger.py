# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU
import BigWorld
from gui.Scaleform.Battle import Battle
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from ModUtils import BattleUtils,MinimapUtils,FileUtils,HotKeysUtils,DecorateUtils
from IngameMessanger import IngameMessanger
import const
import log

class SpotMessanger(object):
    _isActive = True
    _lastActivate = 0

    def setConfig(self, settings):
        self._settings = settings
    
    def initialize(self):
        self._isActive = self._settings['ActiveByDefault']
        self._lastActivate = 0

    def showSixthSenseIndicator(self):
        currentTime = BigWorld.time()
        cooldownTime = self._lastActivate + self._settings['CooldownInterval'] - currentTime
        if cooldownTime > 0:
            log.debug('[time:{:.1f}] activate sixth sense, but it\'s not time yet. (rest {:.1f}s)'.format(currentTime, cooldownTime))
            return
        self._lastActivate = currentTime
        log.debug('[time:{:.1f}] activate sixth sense, do commands.'.format(currentTime))
 
        if self._isActive:
            player = BattleUtils.getPlayer()
            battleTypeName = _getBattleTypeName(player)
            vehicleTypeName = _getVehicleTypeName(player)

            teamAmount = BattleUtils.getTeamAmount(player)
            position = MinimapUtils.getOwnPos(player)

            controllers = IngameMessanger.getChannelControllers()
            for channelType in [ 'team', 'squad' ]:
                if controllers.get(channelType, None):
                    log.debug('controller "{}" found.'.format(channelType))
			
            mode = self._settings.get(battleTypeName, None)
            if not mode:
                log.debug('setting for battle type "{}" is none, use default'.format(battleTypeName))
                mode = self._settings.get('default')

            # vehicle type checks
            if not mode['VehicleTypes'].get(vehicleTypeName, True):
                log.debug('Vehicle type "{}" is disabled.'.format(vehicleTypeName))
                return

            #team amount checks
            maxTeamAmount = mode.get('MaxTeamAmount', 0)
            log.debug('team amount "{}"'.format(teamAmount))
            if maxTeamAmount > 0 and maxTeamAmount < teamAmount:
                log.debug('team amount "{}" is greater than "{}", do nothing.'.format(teamAmount, maxTeamAmount))
                return

            msg = self._settings.get('ImSpotted', None)
            for c in mode['Order']:
                if c == 'ping':
                    log.info('action: "{}", do ping at {}'.format(c, position))
                    IngameMessanger.doPing(controllers.get('team', None), MinimapUtils.name2cell(position))
                elif c == 'help':
                    log.info('action: "{}", call help'.format(c))
                    IngameMessanger.callHelp(controllers.get('team', None))
                elif c == 'teammsg' and msg and msg != 'None':
                    log.info('action: "{}", send message with team channel'.format(c))
                    IngameMessanger.sendText(controllers.get('team', None), msg.format(pos=position))
                elif c == 'squadmsg' and msg and msg != 'None':
                    log.info('action: "{}", send message with squad channel'.format(c))
                    if controllers.has_key('squad'):
                        IngameMessanger.sendText(controllers.get('squad', None), msg.format(pos=position))
                    else:
                        log.info('action: "{}", no squad channel found.'.format(c))

    def toggleActive(self):
        self._isActive = not self._isActive
        if not self._isActive:
            log.debug('Sixth Sense Message disabled')
            BattleUtils.DebugMsg(self._settings['DisableSystemMsg'], True)
        else:
            log.debug('Sixth Sense Message enabled')
            BattleUtils.DebugMsg(self._settings['EnableSystemMsg'], True)


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
