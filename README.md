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

+ config file: res_mods/configs/spotmessanger/spotmessanger.xml
+ document: res_mods/configs/spotmessanger/spotmessanger.txt


ChangeLog
---------
### 0.9-dev
+ disable at observer mode

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
