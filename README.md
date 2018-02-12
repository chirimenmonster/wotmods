![logo](https://user-images.githubusercontent.com/11075065/28247368-bf123140-6a69-11e7-86c3-962ac14bbe95.png)

SpotMessanger
=============
Send message to team or platoon, eventually with a "help" or "ping"
command, if you are spotted and under some conditions.

This mod aim to inform your CW-TC-ESL team if you are spotted but only
if they want that informations:

Infact you can configure the mod to be enabled in some types of
battles and with some types of tanks. Also, in battle you can
disable/enable it pressing F11

All thanks to locastan and BirrettaMalefica for some
explanation and code.


Feature
-------

+ send messages to team when 6th sense
+ cooldown after message, default 60 sec
+ can disable function for some tank types if you want
+ can enable function only when team amount is small, default is always
+ can be different settings for each battle type
+ allows multiple settings for same battle type


Default settings
----------------

+ the message contains the words "An enemy has spotted me at A8"
+ don't ping the minimap
+ use F7 (HELP)
+ F11 to activate/disable the mod
+ NUMPAD4 to reload config
+ enabled for every tank types
+ disabled in random battles except platoon message


Customize
---------

+ config file: mods/configs/chirimen.spotmessanger/config.xml
+ document: mods/configs/chirimen.spotmessanger/customize.txt


Support forum
-------

+ http://forum.worldoftanks.eu/index.php?/topic/562735-092011-/


ChangeLog
---------
### 1.4.0_1
+ repackaging for WoT version 0.9.22.0

### 1.4.0
+ for WoT version 0.9.21.0.3
+ add feature unspotted message (see config-sample4.xml)

### 1.3.2
+ for WoT version 0.9.21.0.2
+ fix bug: error when EnableVehicleType is set and current vehicle type is not included in it

### 1.3.1_6
+ repackaging for WoT version 0.9.21.0.1

### 1.3.1_5
+ repackaging for WoT version 0.9.21.0

### 1.3.1_4
+ repackaging for WoT version 0.9.20.1.4

### 1.3.1_3
+ repackaging for WoT version 0.9.20.1.3

### 1.3.1_2
+ repackaging for WoT version 0.9.20.1.2

### 1.3.1_1
+ repackaging for WoT version 0.9.20.1.1

### 1.3.1
+ for WoT version 0.9.20.1
+ change default config, reload hot key is disabled

### 1.3.0
+ for WoT version 0.9.20.0
+ add to BattleType "Training", "EpicRandom", "EpicRandomTraining"

### 1.2.0_2
+ repackaging for WoT version 0.9.19.1.2

### 1.2.0_1
+ repackaging for WoT version 0.9.19.1.1

### 1.2.0
+ for WoT version 0.9.19.1
+ remove "Company" from BattleType and add "Ranked"

### 1.1.0_1
+ repackaging for WoT version 0.9.19.0.2

### 1.1.0
+ for WoT version 0.9.19.0.1
+ rename wotmod file to conform to the document "World of Tanks: Mod Packages" version 0.4
+ rename configure file to mods/configs/chirimen.spotmessanger/config.xml

### 1.0.0
+ for WoT version 0.9.18.0
+ dont send squad msg, when other members are not alive
+ MaxTeamAmount is excluding myself, so if MaxTeamAmount is 14, always enable
+ refactoring of config strage
+ change code layout

### 0.9.0
+ disable on observer mode and postmortem mode
+ add message to Notification Center, its controllable with config file
+ fix bug: about reload config file

### 0.8.0
+ for WoT version 0.9.17.1
+ add new wotmod package

### 0.7.0
+ for WoT version 0.9.17.0

### 0.6.0
+ for WoT version 0.9.16
+ fix bug

### 0.5.1
+ for WoT version 0.9.15.2

### 0.5.0
+ for WoT version 0.9.15.1
+ many internal changes

### 0.4.0
+ for WoT version 0.9.15.0.1
+ add new parameter LogLevel, for control log output.

### 0.3.0
+ for WoT version 0.9.15.
+ allows multiple settings about same battle type.
+ add new parameter MinTeamAmount, default is 1.

### 0.2.0
+ for WoT version 0.9.14.1.
+ changed style config file.
+ some settings can be set individually for each battle type, random, training, and so on.
+ can be specified order of commands, send chat message, radio command help, minimap ping.
+ add new feature, cooldown interval after sixth sense message, default is 60 sec, only clan wars 30 sec.

### 0.1.0 first release
+ forked form original project of BirrettaMalefica.
+ for WoT version 0.9.14.
+ change install folder, and CameraNode.pyc is obsolete.
