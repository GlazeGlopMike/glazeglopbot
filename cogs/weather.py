# weather.py
import os
import discord
import dotenv
import geopy, geopy.geocoders
import pyowm
import pytz

from datetime import datetime
from discord.ext import commands

def compass_dir(angle):
    """
    Accepts a float angle in [0°,360°).
    Returns a 16-wind direction abbreviation str.
    """
    if angle < 0 or angle >= 360:
        raise ValueError("Bearing not in domain.")
    elif angle < 11.25 or angle >= 348.75:
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

def get_obs(place='', exclude=''):
    """
    Accepts a place string and any parts of the One Call data to ignore.
    Returns a tuple with a PyOWM OneCall object and geopy Location object.

    Default place is Toronto, ON.

    Observation taken using OWM One Call API.
    https://openweathermap.org/api/one-call-api
    
    Geocoding performed with Bing Maps Location API.
    https://docs.microsoft.com/en-us/bingmaps/rest-services/locations/
    """
    # set up weather manager
    dotenv.load_dotenv()
    owm = pyowm.OWM(os.getenv('OWM_TOKEN'))
    mgr = owm.weather_manager()

    # default place is Toronto, ON
    if place.strip() == '':
        place = 'Toronto, ON'

    # find location from search string using Bing Maps
    geocoder = geopy.geocoders.Bing(os.getenv('BING_MAPS_TOKEN'))
    l = geocoder.geocode(place, exactly_one=True, culture='en')
    
    # return weather data and location
    return mgr.one_call(l.latitude, l.longitude, exclude=exclude), l

def uv_emoji(uv):
    """
    Accepts a float UV index value.
    Returns an emoji corresponding to the risk of harm from UV.
    
    See https://openweathermap.org/weather-conditions
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
    Accepts a weather code integer.
    Returns an emoji corresponding to an OpenWeatherMap weather code.
    
    See https://openweathermap.org/weather-conditions
    """
    # thunderstorms
    if int(code / 100) == 2:
        return '\U0001F329'
    # rain
    elif int(code / 100) == 3 or int(code / 100) == 5:
        return '\U0001F327'
    # snow
    elif int(code / 100) == 6:
        return '\u2744'
    # sun
    elif code == 800:
        return '\u2600'
    # few clouds
    elif code >= 801 and code <= 803:
        return '\u26C5'
    # clouds
    elif code == 804:
        return '\u2601'
    # unrecognized code
    else:
        raise ValueError(f"Unrecognized weather ID: '{code}'.")

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
        Sends a weather forecast message.
        Report generated using OpenWeatherMap data for chosen city and time
        frame.
                
        Default location is Toronto, ON and default forecast period is 12h.
        """
        if args:
            if args[0] == '-12h' or args[0] == '-hourly':
                # get observation and location information
                try:
                    place = ' '.join(args[1:])
                    obs, loc = get_obs(place, 'minutely,daily')
                except (AttributeError, geopy.exc.GeocoderQueryError) as e:
                    await ctx.message.add_reaction('\U0001F615');
                    await ctx.send(f"Couldn't get a forecast for that "
                                   "location.")
                except pyowm.commons.exceptions.UnauthorizedError:
                    await ctx.message.add_reaction('\U0001F916');
                    await ctx.send("Couldn't perform the API call.")
                    print("Search failed: Couldn't find OWM token.")

                forecasts = obs.forecast_hourly[:13]
                hours = []
                data = []

                # location details
                loc_str = loc.raw['address']['formattedAddress']

                # time details
                tz = pytz.timezone(obs.timezone)
                current = int(obs.current.reference_time())
                time = datetime.fromtimestamp(int(current), tz)
                time_str = time.strftime('%Y-%m-%d %I:%M %p')

                for f in forecasts[:-1]:
                    # hourly details
                    tz = pytz.timezone(obs.timezone)
                    hour = datetime.fromtimestamp(int(f.reference_time()), tz)
                    hour_str = hour.strftime('%-I %p')

                    # cursory details
                    temp = int(round(f.temperature('celsius')['temp'])) # °C
                    status_emoji = weather_emoji(f.weather_code)
                    pop = int(round(f.precipitation_probability * 100)) # -> %

                    # append data to lists
                    hours.append(hour_str)
                    data.append(f"{status_emoji}\n{temp}°C\nPOP: {pop}%")

                # build embed
                embed = discord.Embed(title=loc_str,
                                      description='Hourly Forecast')

                # generate embed fields
                for i in range(len(hours)):
                    embed.add_field(name=hours[i], value=data[i], inline=True)
                
                # add footer
                embed.set_footer(text=f"Retrieved: {time_str} "
                                 f"({obs.timezone})")
                
                await ctx.send(embed=embed)
            elif args[0] == '-7d' or args[0] == '-daily':
                # get observation and location information
                try:
                    place = ' '.join(args[1:])
                    obs, loc = get_obs(place, 'minutely,hourly')
                except (AttributeError, geopy.exc.GeocoderQueryError) as e:
                    await ctx.message.add_reaction('\U0001F615');
                    await ctx.send(f"Couldn't get a forecast for that "
                                   "location.")
                except pyowm.commons.exceptions.UnauthorizedError:
                    await ctx.message.add_reaction('\U0001F916');
                    await ctx.send("Couldn't perform the API call.")
                    print("Search failed: Couldn't find OWM token.")

                forecasts = obs.forecast_daily
                days = []
                data = []

                # location details
                loc_str = loc.raw['address']['formattedAddress']

                # time details
                tz = pytz.timezone(obs.timezone)
                current = int(obs.current.reference_time())
                time = datetime.fromtimestamp(int(current), tz)
                time_str = time.strftime('%Y-%m-%d %I:%M %p')

                for f in forecasts:
                    # time details
                    date = datetime.fromtimestamp(int(f.reference_time()), tz)
                    date_str = date.strftime('%a %b %-d')

                    # cursory details
                    t = f.temperature('celsius')
                    day_temp = int(round(t['day'])) # °C
                    night_temp = int(round(t['night'])) # °C
                    status_emoji = weather_emoji(f.weather_code)
                    pop = int(round(f.precipitation_probability * 100)) # -> %
                    
                    # append data to lists
                    days.append(date_str)
                    data.append(f"{status_emoji}\nDay: {day_temp}°C\n"
                                f"Night: {night_temp}°C\nPOP: {pop}%")

                # build embed
                embed = discord.Embed(title=loc_str,description='Daily Forecast')

                # generate embed fields
                for i in range(len(days)):
                    embed.add_field(name=days[i], value=data[i], inline=True)
                    
                # add blank field for alignment
                embed.add_field(name='\u200b', value='\u200b', inline=True)

                # add footer
                embed.set_footer(text=f"Retrieved: {time_str} "
                                 f"({obs.timezone})")
                
                await ctx.send(embed=embed)
            elif args[0] == '-current' or args[0] == '-now':
                place = ' '.join(args[1:])
                await self.weather(ctx, place=place)
            else:
                args = ('-12h',) + args
                await self.forecast(ctx, *args)
        else:
            await self.forecast(ctx, '-12h')
    
    @commands.command()
    async def weather(self, ctx, *, place=''):
        """
        Sends a weather report message.
        Report generated using OpenWeatherMap data for chosen city.
                
        Default location is Toronto, ON.
        """
        # get observation and location information
        try:
            obs, loc = get_obs(place, 'minutely,hourly,daily')
        except (AttributeError, geopy.exc.GeocoderQueryError) as e:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"Couldn't get weather for that location.")
        except pyowm.commons.exceptions.UnauthorizedError:
            await ctx.message.add_reaction('\U0001F916');
            await ctx.send("Couldn't perform the API call.")
            print("Search failed: Couldn't find OWM token.")
        
        w = obs.current
        
        # location details
        loc_str = loc.raw['address']['formattedAddress']

        # time details
        tz = pytz.timezone(obs.timezone)
        time = datetime.fromtimestamp(int(w.reference_time()), tz)
        time_str = time.strftime('%Y-%m-%d %I:%M %p')

        # cursory details
        t = w.temperature('celsius') # °C
        temp = int(round(t['temp'])) # °C
        feels_like = int(round(t['feels_like'])) # °C
        dew_point = int(round(w.dewpoint - 273.15)) # K -> °C
        status_emoji = weather_emoji(w.weather_code)

        # other environmental details
        humidity = w.humidity # %
        cloud_cover = w.clouds # %
        uv = round(float(w.uvi), 1) # index
        uv_color = uv_emoji(uv)
        pressure = round(float(w.pressure['press']) * 0.1, 1) # hPa -> kPa
        visibility = round(w.visibility_distance / 1000, 1) # m -> km
        wind_speed = round(float(w.wind()['speed']) * 3.6) # m/s -> km/h
        wind_dir = compass_dir(w.wind()['deg']) # °

        # sun details
        sunrise = datetime.fromtimestamp(int(w.sunrise_time()), tz)
        sunset = datetime.fromtimestamp(int(w.sunset_time()), tz)
        sunrise_str = sunrise.strftime('%-I:%M %p')
        sunset_str = sunset.strftime('%-I:%M %p')

        # build embed
        embed = discord.Embed(title=loc_str)

        # generate embed fields
        embed.add_field(name='At a glance', value=f'{temp}°C {status_emoji}',
                        inline=True)
        embed.add_field(name='Feels like', value=f'{feels_like}°C',
                        inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=True)
        embed.add_field(name='Wind speed', value=f'{wind_speed} km/h {wind_dir}',
                        inline=True)
        embed.add_field(name='Humidity', value=f'{humidity}%', inline=True)
        embed.add_field(name='UV index', value=f'{uv} {uv_color}', inline=True)
        embed.add_field(name='Dew point', value=f'{dew_point}°C', inline=True)
        embed.add_field(name='Visibility', value=f'{visibility} km',
                        inline=True)
        embed.add_field(name='Pressure', value=f'{pressure} kPa', inline=True)
        embed.add_field(name='Sunrise', value=sunrise_str, inline=True)
        embed.add_field(name='Sunset', value=sunset_str, inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=True)

        # add footer
        embed.set_footer(text=f"Retrieved: {time_str} "
                         f"({obs.timezone})")

        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Weather(bot))
