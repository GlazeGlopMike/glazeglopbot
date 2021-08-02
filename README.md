# GlazeGlopBot
## Table of Contents
- [About](#about)
- [Setup](#setup)
- [Usage](#usage)
  - [Commands](#commands)
  - [Command Errors](#command-errors)
  - [Cog Management](#cog-management)
  - [Local Sound Files](#local-sound-files)
- [Cogs](#cogs)
  - [Mod](#mod)
  - [QR](#qr)
  - [RNG](#rng)
  - [VC](#vc)
  - [Weather](#weather)
- [Proposed Features](#proposed-features)
- [License](#license)

## About
GlazeGlopBot is an all-purpose Discord bot written in Python featuring a diverse collection of practical utilities. Fundamentally, commands are organized into independent [discord.py](https://discordpy.readthedocs.io/en/stable/) cogs. Currently, guild moderation, local music playing, (pseudo)random number generation, QR code generation, and weather reporting utilities have been implemented.

On Discord: [@GlazeGlopBot#7510](https://discordapp.com/users/844640688900407327)

## Setup
GlazeGlopBot remains in development and currently serves only a private Discord server for "the boys." Still, you can run your own instance if you'd like!

You can set up your own version of GlazeGlopBot with your own API tokens.

1. Clone the repository.

```git clone https://github.com/GlazeGlopMike/glazeglopbot```

2. Switch to the cloned directory.

```cd glazeglopbot```

3. Install dependencies.

```pip3 install -r requirements.txt```

4. Get your tokens as appropriate.
- Discord token: <https://discord.com/developers>

The weather cog also requires:
- Bing Maps token: <https://www.bingmapsportal.com/>
- OpenWeatherMap token: <https://openweathermap.org/api>

5. Record your own Discord ID. You can get this by right-clicking on your name in any Discord conversation and clicking ```Copy ID```.

6. If you want to use the vc cog, get [FFmpeg](http://ffmpeg.org/download.html).

7. Add the relevant values from steps 4 to 6 into `.env`. If the file doesn't exist, create one with these contents:
```
DISCORD_TOKEN=[Discord token]
BING_MAPS_TOKEN=[Bing Maps token]
OWM_TOKEN=[OpenWeatherMap token]
FFMPEG_PATH=[FFmpeg path]
DEV_IDS=[Discord IDs, comma-separated]
```

8. Add the bot to your guild using the link assigned to it by Discord.

## Usage
### Commands
The bot responds to commands prefixed with the `$` character. Users can be passed as arguments by tagging them. View the full list of commands using `$help`.

GlazeGlopBot also responds to direct messages. Most commands designed for guilds will not work in DMs and others may have reduced functionality.

### Command Errors
If execution of your command was unsuccessful, the bot will react to your message. Errors are classified using emojis:
- :confused: Common errors such as comprehension failure.
- :warning: Some but not all tasks successful.
- :thumbsdown: You don't have permission to use the command.
- :robot: Server-related issue.

### Cog Management
All cogs (`[cog].py` files) in the `cogs` directory are loaded on startup.
- `$ld [cog]` to load a cog
- `$rld [cog]` to reload a cog
- `$rldall` to reload all cogs
- `$uld [cog]` to unload a cog

You can add your own custom-written cogs to the `cogs` folder and load them, as long as there are no cog or command naming conflicts.

Cogs stored in subfolders will also be loaded on startup and reloaded with `$rldall`. These can be individually referenced using `[subfolder].[cog]`.

e.g. `$ld example` to load from `cogs/example.py`

e.g. `$ld subfolder.example` to load from `cogs/subfolder/example.py`.

### Local Sound Files
OGG files (`[name].ogg`) in the `sounds` folder can be played in voice channels using `$sound [name]`. You can add your own too. Audio files in subfolders can be referenced using `[subfolder]/[name]`.

e.g. `$sound example` to play `sounds/example.ogg`

e.g. `$sound subfolder/example` to play `sounds/subfolder/example.ogg`.

A number of my personal compositions are provided as sample sounds. Hope you like them!

## Cogs
### Mod
Some common guild (server) moderation commands. The command author's permissions are verified before execution.
- Muting/deafening users
- Nicknaming users
- Moving users across voice channels
- Disconnecting users from voice channels
- Kicking/banning users
- Pinning messages
- Writing user summaries

### QR
Generates and sends a QR code image using the [pyqrcode](https://pypi.org/project/PyQRCode/) module.

### RNG
Currently features a coin tosser, dice roller and random integer generator.

### VC
Plays sounds from local OGG files or from YouTube. The cog has basic player functions like pausing, resuming, and stopping.

### Weather
GlazeGlopBot grabs weather data through API calls to [OpenWeatherMap](https://openweathermap.org/). To make location input user-friendly, GlazeGlopBot uses the [Bing Maps API](https://www.bingmapsportal.com/) to resolve natural language inputs into geographic coordinates. The weather cog then makes a OneCall request to OWM, which returns information such as temperature, precipitation, air/wind conditions, and sunrise/sunset times. This data is presented using an embed.

The weather cog can grab:
- Current weather
- Tomorrow's forecast
- 12-hour hourly forecast
- 7-day daily forecast

## Proposed Features
- Sound queue system
- Stock summaries
- Standard ↔ Glopesian English translation

## License
Available under the MIT License. See `LICENSE` for more details.
