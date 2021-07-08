# GlazeGlopBot
GlazeGlopBot is a Discord bot intending to convenience members of a private Discord server for the boys. Fundamentally, commands are organized into [discord.py](https://discordpy.readthedocs.io/en/stable/) cogs. Currently, guild moderation and weather reporting utilities have been implemented.

### litwa
A small suite of "inside joke" commands for the boys.

### moderator
Some common guild (server) moderation commands (e.g. moving users across voice channels, disconnecting them, or kicking them from the guild).

### weather
GlazeGlopBot grabs weather data through API calls to [OpenWeatherMap](https://openweathermap.org/). To make location input user-friendly, GlazeGlopBot uses the [Bing Maps API](https://www.bingmapsportal.com/) to resolve natural language inputs into geographic coordinates. The weather cog then makes a OneCall request to OWM, which returns information such as temperature, precipitation, air/wind conditions, and sunrise/sunset times.

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

4. Paste the tokens into the appropriate lines in ```.env```. If the file doesn't exist, create one with the following contents.
```
DISCORD_TOKEN=[Discord token]
BING_MAPS_TOKEN=[Bing Maps token]
OWM_TOKEN=[OpenWeatherMap token]
```

5. Add the bot to your guild using the link assigned to it by Discord.


## Usage
Within Discord guilds, the bot responds to commands prefixed with the ```$``` character (e.g. ```$ree```). Users can be passed as arguments by tagging them.

e.g. ```$bontibi``` to request a greeting.

The bot loads all the cogs (```.py``` files) in the ```cogs``` directory on startup. Individual cogs can be reloaded, unloaded, and loaded with ```$rld```, ```$uld```, and ```$ld``` respectively. To reload all of the cogs, use ```$rldall```. The reloading commands allow updates to the cogs to be applied without restarting the bot.


## Planned Future Additions
- Weather forecasts
- Stock summaries
- Music player
- Voice channel presence with text-to-speech
