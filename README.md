# TavishDeGroot_Bot
## Telegram bot for chat moderation
[![Version](https://img.shields.io/badge/version-0.0.4-green.svg)]()

### Install aiogram
```bash
pip install aiogram
```
## Description

Bot can ban, unban, kick, mute, unmute, warn, unwarn users.
Bot storages info about bans, warns, mutes, nicknames in .JSON files and can show this info in chat by /warnlist, /mutelist, /banlist
Bot can set a nickname for users
### /ban, /unban
"/ban" will permanently ban user
"/unban" will unban user
### /mute, /unmute
"/mute 10m" will mute for 10 minutes, "/mute 50m" will mute for 50 minutes
### /warn /unwarn
"/warn" will add 1 warn for user
3 warns give 24h mute for user
"/unwarn" clears all warns for user
### /kick
"/kick" will kick user out of chat
### /nickname, /mynickname, /profile
"/nickname VeryCoolNickname" will set your nickname
"/mynickname" shows your nickname
"/profile" shows profile picture, nickname, id and join date
