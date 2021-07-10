# GlazeGlopBot
GlazeGlopBot is a Discord bot intending to convenience members of a private Discord server for the boys. Fundamentally, commands are organized into [discord.py](https://discordpy.readthedocs.io/en/stable/) cogs. Currently, guild moderation, random number generator, and weather reporting utilities have been implemented.

### litwa
A small suite of "inside joke" commands for the boys.

### moderator
Some common guild (server) moderation commands (e.g. moving users across voice channels, disconnecting them, or kicking them from the guild).

### rng
Currently features a dice roller and random integer generator.

### vc
Currently limited to playing local sound files. The cog has basic player functions like stopping, pausing, and resuming.

### weather
GlazeGlopBot grabs weather data through API calls to [OpenWeatherMap](https://openweathermap.org/). To make location input user-friendly, GlazeGlopBot uses the [Bing Maps API](https://www.bingmapsportal.com/) to resolve natural language inputs into geographic coordinates. The weather cog then makes a OneCall request to OWM, which returns information such as temperature, precipitation, air/wind conditions, and sunrise/sunset times.

The weather cog can grab:
- Current weather
- 12-hour hourly forecast
- 7-day daily forecast

## Setup
You can set up your own version of GlazeGlopBot with your own API tokens.

1. Clone the repository.
```git clone https://github.com/GlazeGlopMike/glazeglopbot```

2. From the project directory, install dependencies.
```pip3 install -r requirements.txt```

3. Get your tokens as appropriate.
- [Discord Developer Portal](https://discord.com/developers)

The weather cog also requires:
- [Bing Maps Dev Center](https://www.bingmapsportal.com/)
- [OpenWeatherMap](https://openweathermap.org/api)

4. If you want to use the vc cog, get [FFmpeg](http://ffmpeg.org/download.html).

5. Add the values from steps 3 and 4 into ```.env```. If the file doesn't exist, create one with the following contents.
```
DISCORD_TOKEN=[Discord token]
BING_MAPS_TOKEN=[Bing Maps token]
OWM_TOKEN=[OpenWeatherMap token]
FFMPEG_PATH=[FFmpeg path]
```

6. Add the bot to your guild using the link assigned to it by Discord.

## Usage
### Commands
Within Discord guilds, the bot responds to commands prefixed with the ```$``` character (e.g. ```$ree```). Users can be passed as arguments by tagging them.

e.g. ```$bontibi``` to request a greeting.

### Cogs
All the cogs (```[cog].py``` files) in the ```cogs``` directory are loaded on startup.
- ```$ld [cog]``` to load a cog
- ```$rld [cog]``` to reload a cog
- ```$rldall``` to reload all cogs
- ```$uld [cog]``` to unload a cog

You can add your own custom-written cogs to that folder and load them, as long as there are no cog or command naming conflicts.

### Sound
OGG files (```[name].ogg```) in the ```sounds``` folder can be played in voice channels using ```$sound [name]```. You can add your own too.


Updates to ```.env``` can be applied using ```$rldenv```.

## Planned Future Additions
- Built-in help commands
- Stock summaries
- Music player
- Voice channel presence with text-to-speech
