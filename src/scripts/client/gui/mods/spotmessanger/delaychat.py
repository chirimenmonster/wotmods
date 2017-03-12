# -*- coding: utf-8 -*-

# @author: BirrettaMalefica EU, Chirimen SEA

from functools import partial

from logger import log
from wotapi import sysutils, avatarutils, chatutils

class _Delay():
    command = 0.5
    text = 5.0


class DelayChatControl(object):
    
    def __init__(self):
        self._wakeupTime = 0
        self._delay = _Delay()

    def setParam(self, commandDelay=0.5, textDelay=5.0):
        self._delay.command = commandDelay
        self._delay.text = textDelay
        
    def doPing(self, cellIdx):
        self._setCallback(self._delay.command, partial(_CBCommand.doPing, cellIdx))
        return True

    def callHelp(self):
        self._setCallback(self._delay.command, _CBCommand.callHelp)
        return True
    
    def sendTeam(self, text):
        log.debug('send to BATTLE_CHANNEL.TEAM')
        self._setCallback(self._delay.text, partial(_CBCommand.sendTeamChat, text))
        return True

    def sendSquad(self, text):
        if not chatutils.isExistSquadChannel():
            return False
        log.debug('send to BATTLE_CHANNEL.SQUAD')
        self._setCallback(self._delay.text, partial(_CBCommand.sendSquadChat, text))
        return True

    def _setCallback(self, delay, callback):
        currentTime = sysutils.getTime()
        self._wakeupTime = max(self._wakeupTime, currentTime)
        sysutils.setCallback(self._wakeupTime - currentTime, callback)
        self._wakeupTime += delay


class _CBCommand(object):

    @staticmethod
    def doPing(cellIdx):
        if not avatarutils.isPlayerOnArena():
            log.debug('avatar already left arena')
            return
        avatarutils.setForcedGuiControlMode(True)
        chatutils.doPing(cellIdx)
        avatarutils.setForcedGuiControlMode(False)

    @staticmethod
    def callHelp():
        if not avatarutils.isPlayerOnArena():
            log.debug('avatar already left arena')
            return
        chatutils.callHelp()

    @staticmethod
    def sendTeamChat(text):
        if not avatarutils.isPlayerOnArena():
            log.debug('avatar already left arena')
            return
        chatutils.sendTeamChat(text)

    @staticmethod
    def sendSquadChat(text):
        if not avatarutils.isPlayerOnArena():
            log.debug('avatar already left arena')
            return
        channelCtrl.sendSquadChat(text)
