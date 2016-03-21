# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU
from game import *
#import constants
from gui.Scaleform.Battle import Battle
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from ModUtils import BattleUtils,MinimapUtils,FileUtils,HotKeysUtils,DecorateUtils
from Plugin import Plugin
from IngameMessanger import IngameMessanger
import const
import log

class SpotMessanger(Plugin):
    isActive = True

    @staticmethod
    def getBattleTypeName(player):
        import constants
        type = player.arena.guiType
        name = const.BATTLE_TYPE.LABELS.get(type, 'ClanWar')
        log.debug('battle type: ' + name + ' ({}:{})'.format(type, constants.ARENA_GUI_TYPE_LABEL.LABELS[type]))
        return name

    @staticmethod
    def getVehicleTypeName(player):
        type = BattleUtils.getVehicleType(BattleUtils.getCurrentVehicleDesc(player))
        name = const.VEHICLE_TYPE.LABELS[type]
        log.debug('vehicle type: ' + name)
        return name	
		    
    #------ injected methods --------
    @staticmethod
    def showSixthSenseIndicator(self, isShow):
        if isShow and SpotMessanger.isActive:
            player = BattleUtils.getPlayer()
            teamAmount = BattleUtils.getTeamAmount(player)
            position = MinimapUtils.getOwnPos(player)
            controllers = IngameMessanger.getChannelControllers()
            battleTypeName = SpotMessanger.getBattleTypeName(player)
			
            setting = SpotMessanger.settings.get(battleTypeName, None)
            if not setting:
                log.debug('setting for battle type "{}" is none, use default'.format(battleTypeName))
                setting = SpotMessanger.settings.get('default')

            # vehicle type checks
            vehicleTypeName = SpotMessanger.getVehicleTypeName(player)
            if not setting['VehicleTypes'].get(vehicleTypeName, True):
                log.debug('Vehicle type "{}" is disabled.'.format(vehicleTypeName))
                return

            #team amount checks
            maxTeamAmount = setting.get('MaxTeamAmount', 0)
            log.debug('team amount "{}"'.format(teamAmount))
            if maxTeamAmount > 0 and maxTeamAmount < teamAmount:
                log.debug('team amount "{}" is greater than "{}", do nothing.'.format(teamAmount, maxTeamAmount))
                return

            msg = SpotMessanger.settings.get('ImSpotted', None)
            if controllers.get('team', None):
                log.debug('controller "team" found.')
            if controllers.get('squad', None):
                log.debug('controller "squad" found.')
            for c in setting['Order']:
                if c == 'ping':
                    log.debug('action: "{}", do ping at {}'.format(c, position))
                    IngameMessanger.doPing(controllers.get('team', None), MinimapUtils.name2cell(position))
                elif c == 'help':
                    log.debug('action: "{}", call help'.format(c))
                    IngameMessanger.callHelp(controllers.get('team', None))
                elif c == 'teammsg' and msg and msg != 'None':
                    log.debug('action: "{}", send message with team channel'.format(c))
                    IngameMessanger.sendText(controllers.get('team', None), msg.format(pos=position))
                elif c == 'squadmsg' and msg and msg != 'None':
                    log.debug('action: "{}", send message with squad channel'.format(c))
                    if controllers.has_key('squad'):
                        IngameMessanger.sendText(controllers.get('squad', None), msg.format(pos=position))
                    else:
                        log.debug('action: "{}", no squad channel found.'.format(c))

    @staticmethod
    def handleActivationHotkey():
        if SpotMessanger.isActive:
            log.debug('Sixth Sense Message disabled')
            BattleUtils.DebugMsg(SpotMessanger.settings['DisableSystemMsg'], True)
        else:
            log.debug('Sixth Sense Message enabled')
            BattleUtils.DebugMsg(SpotMessanger.settings['EnableSystemMsg'], True)
        SpotMessanger.isActive = not SpotMessanger.isActive
        
    #--------- end ---------
