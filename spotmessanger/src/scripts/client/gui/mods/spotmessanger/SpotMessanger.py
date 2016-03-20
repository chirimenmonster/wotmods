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
    pluginName = 'SpotMessanger'
    confFile = '../res_mods/configs/spotmessanger/spotmessanger.xml'
    myConf = {
        'ActiveByDefault':True,
        'ActivationHotkey':'KEY_F11',
        'ReloadConfigKey':'KEY_NUMPAD4',
        'DoPing':False,
        'CallHelp':False,
        'ImSpotted':'I\'m spotted at {pos}',
        'EnableSystemMsg':'enabled',
        'DisableSystemMsg':'disabled',
        'TryPlatoonMes':False,
        'AvoidRandomMes':True,
        'AvoidTrainingMes':False,
        'AvoidCompanyMes':False,
        'AvoidCyberSportMes':False,
        'AvoidClanWarMes':False,
        'AvoidFortificationsMes':False,
        'OnTD':True,
        'OnMD':True,
        'OnHT':True,
        'OnLT':True,
        'OnSPG':True,
        'MaxTeamAmountOnRandom':0,
        'MaxTeamAmountOnTraining':0,
        'MaxTeamAmountOnCompany':0,
        'MaxTeamAmountOnCyberSport':0,
        'MaxTeamAmountOnFortifications':0,
        'MaxTeamAmountOnClanWar':0,
        'pluginEnable' : True
        } 
	
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
		
    @staticmethod
    def getController(player):
        controller = None
	
        #battle type checks
        battleTypeName = SpotMessanger.getBattleTypeName(player)
        controllers = IngameMessanger.getChannelControllers()
        if battleTypeName == 'Random' and SpotMessanger.myConf.get('TryPlatoonMes', False):
            controller = controllers.get('squad', None)
        if not controller and not SpotMessanger.myConf.get('Avoid' + battleTypeName + 'Mes', False):
            controller = controllers.get('team', None)
        
        #vehicle type checks
        vehicleTypeName = SpotMessanger.getVehicleTypeName(player)
        if not SpotMessanger.myConf.get('On' + vehicleTypeName, True):
            controller = None
        
        #team amount checks
        maxTeamAmount = SpotMessanger.myConf.get('MaxTeamAmountOn' + battleTypeName, 0)
        if maxTeamAmount > 0 and maxTeamAmount < BattleUtils.getTeamAmount(player):
            controller = None
        
        return controller
    
    #------ injected methods --------
    @staticmethod
    def showSixthSenseIndicator(self, isShow):
        if isShow and SpotMessanger.isActive:
            player = BattleUtils.getPlayer()
            position = MinimapUtils.getOwnPos(player)
            text = SpotMessanger.myConf.get('ImSpotted', 'None')
            controller = SpotMessanger.getController(player)
            if controller:
                if text != 'None' and text:
                    log.debug('action: send message')
                    IngameMessanger.sendText(controller, text.format(pos=position))
                if SpotMessanger.myConf['DoPing']:
                    log.debug('action: do ping')
                    IngameMessanger.doPing(controller)
                if SpotMessanger.myConf['CallHelp']:
                    log.debug('action: call help')
                    IngameMessanger.callHelp(controller)

    @staticmethod
    def handleActivationHotkey():
        if SpotMessanger.isActive:
            log.debug('Sixth Sense Message disabled')
            BattleUtils.DebugMsg(SpotMessanger.myConf['DisableSystemMsg'], True)
        else:
            log.debug('Sixth Sense Message enabled')
            BattleUtils.DebugMsg(SpotMessanger.myConf['EnableSystemMsg'], True)
        SpotMessanger.isActive = not SpotMessanger.isActive
        
    #--------- end ---------

    @classmethod
    def readConfig(cls):
        super(SpotMessanger, SpotMessanger).readConfig()
        SpotMessanger.isActive = SpotMessanger.myConf['ActiveByDefault']
