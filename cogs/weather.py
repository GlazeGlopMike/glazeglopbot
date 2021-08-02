# weather.py
import os
import discord
import dotenv
import geopy, geopy.geocoders
import pyowm
import pytz

from datetime import datetime
from discord.ext import commands
from discord import Embed

def compass_dir(angle):
    """
    Accepts angle in degrees.
    Returns 16-wind direction abbreviation.
    """
    angle %= 360
    
    if angle < 11.25 or angle >= 348.75:
        return 'N'
    elif angle < 33.75:
        return 'NNE'
    elif angle < 56.25:
        return 'NE'
    elif angle < 78.75:
        return 'ENE'
    elif angle < 101.25:
        return 'E'
    elif angle < 123.75:
        return 'ESE'
    elif angle < 146.25:
        return 'SE'
    elif angle < 168.75:
        return 'SSE'
    elif angle < 191.25:
        return 'S'
    elif angle < 213.75:
        return 'SSW'
    elif angle < 236.25:
        return 'SW'
    elif angle < 258.75:
        return 'WSW'
    elif angle < 281.25:
        return 'W'
    elif angle < 303.75:
        return 'WNW'
    elif angle < 326.25:
        return 'NW'
    elif angle < 348.75:
        return 'NNW'

async def get_obs_loc(place='', *, exclude=''):
    """
    Accepts place and JSON arguments for One Call data to ignore.
    Returns tuple with PyOWM OneCall and geopy Location.

    Default place is Toronto, ON.

    Observation taken using OWM One Call API.
    https://openweathermap.org/api/one-call-api
    
    Geocoding performed with Bing Maps Location API.
    https://docs.microsoft.com/en-us/bingmaps/rest-services/locations/
    """
    # set up weather manager
    dotenv.load_dotenv()
    owm = pyowm.OWM(os.environ['OWM_TOKEN'])
    mgr = owm.weather_manager()

    # default place is Toronto, ON
    if not place.strip():
        place = 'Toronto, ON'

    # find location from search string using Bing Maps
    geocoder = geopy.geocoders.Bing(os.getenv('BING_MAPS_TOKEN'))
    l = geocoder.geocode(place, exactly_one=True, culture='en')
    
    # return weather data and location
    return mgr.one_call(l.latitude, l.longitude, exclude=exclude), l

def uv_emoji(uv):
    """
    Accepts UV index value.
    Returns colour emoji corresponding to risk of harm.
    
    See https://en.wikipedia.org/wiki/Ultraviolet_index#Index_usage
    """
    # negative values
    if uv < 0:
        raise ValueError("UV index cannot be negative.")
    # low -> green
    elif uv <= 2:
        return '\U0001F7E9'
    # moderate -> yellow
    elif uv <= 5:
        return '\U0001F7E8'
    # high -> orange
    elif uv <= 7:
        return '\U0001F7E7'
    # very high -> red
    elif uv <= 10:
        return '\U0001F7E5'
    # extreme -> violet
    else:
        return '\U0001F7EA'

def weather_emoji(code):
    """
    Accepts weather code integer.
    Returns emoji corresponding to OpenWeatherMap weather code.
    
    See https://openweathermap.org/weather-conditions
    Emojis differ from OpenWeatherMap icons.
    """
    first = int(code / 100)
    
    # thunderstorms
    if first == 2:
        return '\U0001F329'
    # shower rain
    elif first == 3 or 500 <= code <= 504:
        return '\U0001F327'
    # rain
    elif first == 5:
        return '\U0001F326'
    # snow
    elif first == 6:
        return '\u2744'
    # fog
    elif first == 7:
        return '\U0001F32B'
    # sun
    elif code == 800:
        return '\u2600'
    # few clouds
    elif code == 801:
        return '\u26C5'
    # clouds
    elif code >= 802:
        return '\u2601'
    # unrecognized code
    else:
        raise ValueError(f"Unrecognized weather ID: '{code}'.")

def current_weather_embed(obs, loc):
    """
    Accepts pyowm OneCall and geopy Location.
    Returns Embed for weather report.
    """
    # weather details
    w = obs.current
    loc_str = loc.raw['address']['formattedAddress']
    tz = pytz.timezone(obs.timezone)
    time = datetime.fromtimestamp(w.reference_time(), tz)
    time_str = time.strftime('%Y-%m-%d %I:%M %p')
    
    t = w.temperature('celsius') # °C
    temp = int(round(t['temp'])) # °C
    status_emoji = weather_emoji(w.weather_code)
    feels_like = int(round(t['feels_like'])) # °C
    pop = int(round(obs.forecast_hourly[0].precipitation_probability * 100)) # %

    wind_speed = round(float(w.wind()['speed']) * 3.6) # m/s -> km/h
    wind_dir = compass_dir(w.wind()['deg']) # °
    humidity = w.humidity # %
    uv = round((w.uvi)) # index
    uv_color = uv_emoji(uv)
    
    dew_point = int(round(w.dewpoint - 273.15)) # K -> °C
    visibility = round(w.visibility_distance / 1000, 1) # m -> km
    pressure = round(float(w.pressure['press']) * 0.1, 1) # hPa -> kPa
    
    sunrise = datetime.fromtimestamp(w.sunrise_time(), tz)
    sunset = datetime.fromtimestamp(w.sunset_time(), tz)
    
    # build embed
    embed = Embed(title=loc_str)
    embed.add_field(name='At a glance', value=f'{temp}°C {status_emoji}',
                    inline=True)
    embed.add_field(name='Feels like', value=f'{feels_like}°C',
                    inline=True)
    embed.add_field(name='POP', value=f'{pop}%', inline=True)
    
    embed.add_field(name='Wind speed', value=f'{wind_speed} km/h {wind_dir}',
                    inline=True)
    embed.add_field(name='Humidity', value=f'{humidity}%', inline=True)
    embed.add_field(name='UV index', value=f'{uv} {uv_color}', inline=True)
    
    embed.add_field(name='Dew point', value=f'{dew_point}°C', inline=True)
    embed.add_field(name='Visibility', value=f'{visibility} km', inline=True)
    embed.add_field(name='Pressure', value=f'{pressure} kPa', inline=True)
    
    embed.add_field(name='Sunrise', value=sunrise.strftime('%-I:%M %p'),
                    inline=True)
    embed.add_field(name='Sunset', value=sunset.strftime('%-I:%M %p'),
                    inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=True)
    embed.set_footer(text=f"Retrieved: {time_str} ({obs.timezone})")
    
    return embed

def daily_forecast_embed(obs, loc):
    """
    Accepts pyowm OneCall and geopy Location.
    Returns Embed for 7-day forecast.
    """
    # forecast details
    forecasts = obs.forecast_daily
    loc_str = loc.raw['address']['formattedAddress']
    tz = pytz.timezone(obs.timezone)
    time = datetime.fromtimestamp(obs.current.reference_time(), tz)
    time_str = time.strftime('%Y-%m-%d %I:%M %p')

    days = []
    data = []

    for f in forecasts:
        date = datetime.fromtimestamp(f.reference_time(), tz)
        date_str = date.strftime('%a %b %-d')
        t = f.temperature('celsius')
        day_temp = int(round(t['day'])) # °C
        night_temp = int(round(t['night'])) # °C
        status_emoji = weather_emoji(f.weather_code)
        pop = int(round(f.precipitation_probability * 100)) # -> %
        
        days.append(date_str)
        data.append(f"{status_emoji}\nDay: {day_temp}°C\n"
                    f"Night: {night_temp}°C\nPOP: {pop}%")

    # build embed
    embed = Embed(title=loc_str,description='Daily Forecast')
    
    for i in range(8):
        embed.add_field(name=days[i], value=data[i], inline=True)
    
    embed.add_field(name='\u200b', value='\u200b', inline=True)
    embed.set_footer(text=f"Retrieved: {time_str} ({obs.timezone})")
    
    return embed

def hourly_forecast_embed(obs, loc):
    """
    Accepts pyowm OneCall and geopy Location.
    Returns Embed for 12-hour forecast.
    """
    # forecast details
    forecasts = obs.forecast_hourly[:12]
    loc_str = loc.raw['address']['formattedAddress']
    tz = pytz.timezone(obs.timezone)
    time = datetime.fromtimestamp(obs.current.reference_time(), tz)
    time_str = time.strftime('%Y-%m-%d %I:%M %p')

    hours = []
    data = []
    
    for f in forecasts:
        tz = pytz.timezone(obs.timezone)
        hour = datetime.fromtimestamp(f.reference_time(), tz)
        hour_str = hour.strftime('%-I %p')
        temp = int(round(f.temperature('celsius')['temp'])) # °C
        status_emoji = weather_emoji(f.weather_code)
        pop = int(round(f.precipitation_probability * 100)) # -> %
        
        hours.append(hour_str)
        data.append(f"{status_emoji}\n{temp}°C\nPOP: {pop}%")

    # build embed
    embed = Embed(title=loc_str, description='Hourly Forecast')

    for i in range(12):
        embed.add_field(name=hours[i], value=data[i], inline=True)
    
    embed.set_footer(text=f"Retrieved: {time_str} ({obs.timezone})")
    
    return embed

def tomorrow_forecast_embed(obs, loc):
    """
    Accepts pyowm OneCall and geopy Location.
    Returns Embed for tomorrow's forecast.
    """
    # weather details
    w = obs.forecast_daily[1]
    loc_str = loc.raw['address']['formattedAddress']
    tz = pytz.timezone(obs.timezone)
    time = datetime.fromtimestamp(obs.current.reference_time(), tz)
    time_str = time.strftime('%Y-%m-%d %I:%M %p')

    date = datetime.fromtimestamp(w.reference_time(), tz)
    date_str = date.strftime('%A, %B %-d')
    
    t = w.temperature('celsius') # °C
    day_temp = int(round(t['day'])) # °C
    status_emoji = weather_emoji(w.weather_code)
    feels_like = int(round(t['feels_like_day'])) # °C
    pop = int(round(w.precipitation_probability * 100)) # %
    
    morn_temp = int(round(t['morn'])) # °C
    eve_temp = int(round(t['eve'])) # °C
    night_temp = int(round(t['night'])) # °C
    
    humidity = w.humidity # %
    uv = round((w.uvi)) # index
    uv_color = uv_emoji(uv)
    
    sunrise = datetime.fromtimestamp(w.sunrise_time(), tz)
    sunset = datetime.fromtimestamp(w.sunset_time(), tz)
    
    # build embed
    embed = Embed(title=loc_str, description=f'Forecast for {date_str}')
    embed.add_field(name='At a glance', value=f'{day_temp}°C {status_emoji}',
                    inline=True)
    embed.add_field(name='Feels like', value=f'{feels_like}°C',
                    inline=True)
    embed.add_field(name='POP', value=f'{pop}%', inline=True)
    
    embed.add_field(name='Morning', value=f'{morn_temp}°C', inline=True)
    embed.add_field(name='Evening', value=f'{eve_temp}°C', inline=True)
    embed.add_field(name='Night', value=f'{night_temp}°C', inline=True)

    embed.add_field(name='Humidity', value=f'{humidity}%', inline=True)
    embed.add_field(name='UV index', value=f'{uv} {uv_color}', inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=True)
    
    embed.add_field(name='Sunrise', value=sunrise.strftime('%-I:%M %p'),
                    inline=True)
    embed.add_field(name='Sunset', value=sunset.strftime('%-I:%M %p'),
                    inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=True)
    embed.set_footer(text=f"Retrieved: {time_str} ({obs.timezone})")
    
    return embed

class Weather(commands.Cog):
    """
    Cog wrapping weather-related commands.
    
    Weather obtained using OpenWeatherMap data.
    https://openweathermap.org/
    """
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['fc'])
    async def forecast(self, ctx, *args):
        """
        Sends weather forecast message.
        Report generated using OpenWeatherMap data for chosen city and time
        frame.
                
        Default location is Toronto, ON and default forecast period is daily.
        """
        if args:
            place = ' '.join(args[1:])

            try:
                if args[0] == '-current' or args[0] == '-now':
                    obs, loc = await get_obs_loc(place,
                                                 exclude='minutely,daily')
                    await ctx.send(embed=current_weather_embed(obs, loc))
                elif args[0] == '-tmrw' or args[0] == '-tomorrow':
                    obs, loc = await get_obs_loc(place,
                                                 exclude='minutely,hourly')
                    await ctx.send(embed=tomorrow_forecast_embed(obs, loc))
                elif args[0] == '-7d' or args[0] == '-daily':
                    obs, loc = await get_obs_loc(place,
                                                 exclude='minutely,hourly')
                    await ctx.send(embed=daily_forecast_embed(obs, loc)) 
                elif args[0] == '-12h' or args[0] == '-hourly':
                    obs, loc = await get_obs_loc(place,
                                                 exclude='minutely,daily')
                    await ctx.send(embed=hourly_forecast_embed(obs, loc))
                else:
                    await self.forecast(ctx, '-7d', args[0], place)
            except geopy.exc.GeocoderAuthenticationFailure:
                await ctx.message.add_reaction('\U0001F916');
                await ctx.send("Couldn't geocode due to missing token.")
                print("Search failed: Need a valid Bing Maps token.")
            except (AttributeError, geopy.exc.GeocoderQueryError) as e:
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("Couldn't get weather for that location.")
            except pyowm.commons.exceptions.UnauthorizedError:
                await ctx.message.add_reaction('\U0001F916');
                await ctx.send("Couldn't get weather due to missing token.")
                print("Search failed: Need a valid OWM token.")
        else:
            await self.forecast(ctx, '-7d')
    
    @commands.command()
    async def weather(self, ctx, *, place=''):
        """
        Sends weather report message.
        Report generated using OpenWeatherMap data for chosen city.
                
        Default location is Toronto, ON.
        """
        await self.forecast(ctx, '-now', place)
        
def setup(bot):
    bot.add_cog(Weather(bot))
