# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU
from game import *
#import constants
from gui.Scaleform.Battle import Battle
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_NOTE
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
        if type in const.BATTLE_TYPE.LABELS:
            name = const.BATTLE_TYPE.LABELS[type]
        else:
            name = 'ClanWar'
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
        battleType = player.arena.guiType
        battleTypeName = SpotMessanger.getBattleTypeName(player)
        if battleTypeName in 'Random' and SpotMessanger.myConf['TryPlatoonMes']:
            if IngameMessanger().hasSquadChannelController():
                controller = IngameMessanger().getSquadChannelController()
        if not controller:
            key = 'Avoid' + battleTypeName + 'Mes'
            if not SpotMessanger.myConf.has_key(key) or not SpotMessanger.myConf[key]:
                controller = IngameMessanger().getTeamChannelController()
        
        #vehicle type checks
        vehicleTypeName = SpotMessanger.getVehicleTypeName(player)
        if not SpotMessanger.myConf['On' + vehicleTypeName]:
            return None
        
        #team amount checks
        if controller:
            key = 'MaxTeamAmountOn' + battleTypeName
            if SpotMessanger.myConf.has_key(key):
                maxTeamAmount = SpotMessanger.myConf[key]
                if maxTeamAmount > 0 and maxTeamAmount < BattleUtils.getTeamAmount(player):
                    return None
        
        return controller

    @staticmethod
    def myDoPing(controller,position):
        if controller and SpotMessanger.myConf['DoPing']:
            IngameMessanger().doPing(controller,MinimapUtils.name2cell(position))
            
    @staticmethod
    def myCallHelp(controller):
        if controller and SpotMessanger.myConf['CallHelp']:
            IngameMessanger().callHelp(controller)
    
    @staticmethod
    def mySendMessage(controller,text):
        if text != "None" and text and controller:
            IngameMessanger().sendText(controller,text)
    
    #------ injected methods --------
    @staticmethod
    def showSixthSenseIndicator(self, isShow):
        if isShow and SpotMessanger.isActive:
            player = BattleUtils.getPlayer()
            position = MinimapUtils.getOwnPos(player)
            text = SpotMessanger.myConf['ImSpotted']
            controller = SpotMessanger.getController(player)
            SpotMessanger.mySendMessage(controller,text.replace("{pos}", position+""))
            SpotMessanger.myDoPing(controller,position)
            SpotMessanger.myCallHelp(controller)                   
    
    @staticmethod
    def handleActivationHotkey():
        if SpotMessanger.isActive:
            BattleUtils.DebugMsg(SpotMessanger.myConf['DisableSystemMsg'], True)
        else:
            BattleUtils.DebugMsg(SpotMessanger.myConf['EnableSystemMsg'], True)
        SpotMessanger.isActive = not SpotMessanger.isActive
        
    #--------- end ---------
    @classmethod
    def run(cls):
        super(SpotMessanger, SpotMessanger).run()
        cls.addEventHandler(SpotMessanger.myConf['ReloadConfigKey'],cls.reloadConfig)
        cls.addEventHandler(SpotMessanger.myConf['ActivationHotkey'],SpotMessanger.handleActivationHotkey)

    @classmethod
    def readConfig(cls):
        super(SpotMessanger, SpotMessanger).readConfig()
        SpotMessanger.isActive = SpotMessanger.myConf['ActiveByDefault']
