# GlazeGlopBot
GlazeGlopBot is a Discord bot intending to convenience members of a private Discord server for the boys. Fundamentally, commands are organized into [discord.py](https://discordpy.readthedocs.io/en/stable/) cogs. Currently, guild moderation and weather reporting utilities have been implemented.

### litwa
A small suite of "inside joke" commands for the boys.

### moderator
Some common guild (server) moderation commands (e.g. moving users across voice channels, disconnecting them, or kicking them from the guild).

### weather
GlazeGlopBot grabs weather data through API calls to [OpenWeatherMap](https://openweathermap.org/). To make location input user-friendly, GlazeGlopBot uses the [Bing Maps API](https://www.bingmapsportal.com/) to resolve natural language inputs into geographic coordinates. The weather cog then makes a OneCall request to OWM, which returns information such as temperature, precipitation, air/wind conditions, and sunrise/sunset times.

## Setup
Setup instructions and aids coming soon.

## Usage
Within Discord guilds, the bot responds to commands prefixed with the ```$``` character (e.g. ```$ree```). Users can be passed as arguments by tagging them.

## Possible Additions
- Weather forecasts
- Stock summaries
- Music player
- Voice channel presence with text-to-speech
