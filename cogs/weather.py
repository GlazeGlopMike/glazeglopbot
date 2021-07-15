# weather.py
import os
import discord
import dotenv
import geopy, geopy.geocoders
import pyowm
import pytz

from datetime import datetime
from discord.ext import commands

class Weather(commands.Cog):
    """
    Cog wrapping weather-related commands.
    
    Weather obtained using OpenWeatherMap data.
    https://openweathermap.org/
    """
    def __init__(self, bot):
        self.bot = bot
    
    def compass_dir(self, angle):
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
    
    def get_obs(self, place='', exclude=''):
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
        
    
    def weather_emoji(self, w):
        """
        Accepts a Weather object.
        Returns an emoji corresponding to an OpenWeatherMap weather code
        
        See https://openweathermap.org/weather-conditions
        """
        # thunderstorms
        if int(w.weather_code / 100) == 2:
            return '\U0001F329'
        # rain
        elif int(w.weather_code / 100) == 3 or int(w.weather_code / 100) == 5:
            return '\U0001F327'
        # snow
        elif int(w.weather_code / 100) == 6:
            return '\u2744'
        # sun
        elif w.weather_code == 800:
            return '\u2600'
        # few clouds
        elif w.weather_code >= 801 and w.weather_code <= 803:
            return '\u26C5'
        # clouds
        elif w.weather_code == 804:
            return '\u2601'
        # unrecognized code
        else:
            raise ValueError("Unrecognized weather ID.")

    @commands.command(aliases=['fc'])
    async def forecast(self, ctx, *args):
        """
        Sends a weather forecast message using OpenWeatherMap data for
        chosen city and time frame.
                
        Default location is Toronto, ON and default forecast period is 12h.
        """
        if args:
            if args[0] == '-12h' or args[0] == '-hourly':
                # get observation and location information
                try:
                    place = ' '.join(args[1:])
                    obs, loc = self.get_obs(place, 'minutely,daily')
                except (AttributeError, geopy.exc.GeocoderQueryError) as e:
                    await ctx.message.add_reaction('\U0001F615');
                    await ctx.send(f"Couldn't get a forecast for that "
                                   "location.")
                except pyowm.commons.exceptions.UnauthorizedError:
                    await ctx.message.add_reaction('\U0001F916');
                    await ctx.send("Couldn't perform the API call.")
                    print("Search failed: Couldn't find OWM token.")

                forecasts = obs.forecast_hourly[:13]
                f_list = []

                # location details
                loc_str = loc.raw['address']['formattedAddress']

                for f in forecasts:
                    # time details
                    tz = pytz.timezone(obs.timezone)
                    time = datetime.fromtimestamp(int(f.reference_time()), tz)
                    time_str = time.strftime('%-I %p')

                    # cursory details
                    temp = int(round(f.temperature('celsius')['temp'])) # °C
                    status_emoji = self.weather_emoji(f)
                    pop = int(round(f.precipitation_probability * 100)) # -> %
                    
                    f_list.append(f"{time_str} | {temp}°C {status_emoji} | "
                                  f"POP: {pop}%")

                f_str = '\n'.join(f_list)
                await ctx.send(f">>> {loc_str}\n{f_str}")
            elif args[0] == '-7d' or args[0] == '-daily':
                # get observation and location information
                try:
                    place = ' '.join(args[1:])
                    obs, loc = self.get_obs(place, 'minutely,hourly')
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
                    status_emoji = self.weather_emoji(f)
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
    
    @commands.command(aliases=['wr'])
    async def weather(self, ctx, *, place=''):
        """
        Sends a weather report message using OpenWeatherMap data for
        chosen city.
                
        Default location is Toronto, ON.
        """
        # get observation and location information
        try:
            obs, loc = self.get_obs(place, 'minutely,hourly,daily')
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
        status_emoji = self.weather_emoji(w)

        # other environmental details
        humidity = w.humidity # %
        cloud_cover = w.clouds # %
        uv = round(float(w.uvi), 1) # index
        pressure = round(float(w.pressure['press']) * 0.1, 1) # hPa -> kPa
        visibility = round(w.visibility_distance / 1000, 1) # m -> km
        wind_speed = round(float(w.wind()['speed']) * 3.6) # m/s -> km/h
        wind_dir = self.compass_dir(w.wind()['deg']) # °

        # sun details
        sunrise = datetime.fromtimestamp(int(w.sunrise_time()), tz)
        sunset = datetime.fromtimestamp(int(w.sunset_time()), tz)
        sunrise_str = sunrise.strftime('%I:%M %p')
        sunset_str = sunset.strftime('%I:%M %p')
        
        await ctx.send(f">>> {loc_str} | {temp}°C {status_emoji}\n"
                        f"Feels like: {feels_like}°C | "
                        f"Humidity: {humidity}% | "
                        f"Wind: {wind_speed} km/h {wind_dir}\n"
                        f"Clouds: {cloud_cover}% | UV: {uv} | "
                        f"Visibility: {visibility} km\n"
                        f"Dew point: {dew_point}°C | "
                        f"Pressure: {pressure} kPa\n"
                        f"Sunrise: {sunrise_str} | Sunset: {sunset_str}\n"
                        f"Updated {time_str} "
                        f"({obs.timezone})")
        
def setup(bot):
    bot.add_cog(Weather(bot))
