# GlazeGlopBot
GlazeGlopBot is an all-purpose Discord bot written in Python featuring a diverse collection of practical utilities. Fundamentally, commands are organized into [discord.py](https://discordpy.readthedocs.io/en/stable/) cogs. Currently, guild moderation, (pseudo)random number generation, QR code generation, and weather reporting utilities have been implemented.

## Cogs
### Mod
Some common guild (server) moderation commands. The command author's server permissions are verified before execution.
- Muting/deafening users
- Nicknaming users
- Pinning messages
- Moving users across voice channels
- Disconnecting users from voice channels
- Kicking/banning users

### QR
Generates and sends a QR code image using the [pyqrcode](https://pypi.org/project/PyQRCode/) module.

### RNG
Currently features a dice roller and random integer generator.

### VC
Currently limited to playing local sound files. The cog has basic player functions like stopping, pausing, and resuming.

### Weather
GlazeGlopBot grabs weather data through API calls to [OpenWeatherMap](https://openweathermap.org/). To make location input user-friendly, GlazeGlopBot uses the [Bing Maps API](https://www.bingmapsportal.com/) to resolve natural language inputs into geographic coordinates. The weather cog then makes a OneCall request to OWM, which returns information such as temperature, precipitation, air/wind conditions, and sunrise/sunset times. This data is presented using an embed.

The weather cog can grab:
- Current weather
- Tomorrow's forecast
- 12-hour hourly forecast
- 7-day daily forecast

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

5. If you want to use the vc cog, get [FFmpeg](http://ffmpeg.org/download.html).

6. Add the values from steps 3 and 4 into ```.env```. If the file doesn't exist, create one with these contents:
```
DISCORD_TOKEN=[Discord token]
BING_MAPS_TOKEN=[Bing Maps token]
OWM_TOKEN=[OpenWeatherMap token]
FFMPEG_PATH=[FFmpeg path]
```

7. Add the bot to your guild using the link assigned to it by Discord.

## Usage
### Commands
The bot responds to commands prefixed with the ```$``` character. Users can be passed as arguments by tagging them. View the list of commands using ```$help```.

GlazeGlopBot also responds to direct messages. Most commands implemented for guilds will not work in DMs and some other commands may have reduced functionality.

### Cogs
All cogs (```[cog].py``` files) in the ```cogs``` directory are loaded on startup.
- ```$ld [cog]``` to load a cog
- ```$rld [cog]``` to reload a cog
- ```$rldall``` to reload all cogs
- ```$uld [cog]``` to unload a cog

You can add your own custom-written cogs to ```cogs``` and load them, as long as there are no cog or command naming conflicts.

Cogs stored in subfolders will also be loaded on startup and reloaded with ```$rldall```. These can be individually referenced using ```[subfolder].[cog]```.

e.g. ```$ld subfolder.example``` to reload ```cogs/subfolder/example.py```.

### Environment File
Updates to ```.env``` can be applied using ```$rldenv```. See steps 4 to 7 in [Setup](#setup) for more details.

### Sound
OGG files (```[name].ogg```) in the ```sounds``` folder can be played in voice channels using ```$sound [name]```. You can add your own too.

## Planned Future Updates
- Channel-specific permission verification
- Music streaming from YouTube
- Restricting cog handling commands to whitelisted Discord IDs
- Stock summaries
- Translation between Standard and Glopesian English
