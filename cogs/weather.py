# weather.py
import datetime
import os

from discord.ext import commands
import dotenv
import geopy, geopy.geocoders
import pyowm
import pytz

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
    
    def get_obs(self, city, exclude = ''):
        """
        Accepts a place string and any parts of the One Call data to ignore.
        Returns a tuple with a PyOWM OneCall object and geopy Location object.

        Observation taken using OWM One Call API.
        https://openweathermap.org/api/one-call-api
        
        Geocoding performed with Bing Maps Location API.
        https://docs.microsoft.com/en-us/bingmaps/rest-services/locations/
        """
        # set up weather manager
        dotenv.load_dotenv()
        owm = pyowm.OWM(os.getenv('OWM_TOKEN'))
        mgr = owm.weather_manager()

        # find location from search string using Bing Maps
        geocoder = geopy.geocoders.Bing(os.getenv('BING_MAPS_TOKEN'))
        l = geocoder.geocode(city, exactly_one=True, culture='en')
        
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
    
    @commands.command()
    async def weather(self, ctx, *, place='Toronto, ON'):
        """
        Sends a weather report message using OpenWeatherMap data for
        chosen city.
                
        Default location is Toronto, ON.
        """

        # get observation and location information
        obs, loc = None, None
        
        try:
            obs, loc = self.get_obs(place, 'minutely,hourly,daily')
        except AttributeError:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"Couldn't find weather for that location.")
        except pyowm.commons.exceptions.UnauthorizedError:
            await ctx.message.add_reaction('\U0001F916');
            await ctx.send("Couldn't perform the API call.")
            print("Search failed: Couldn't find OWM token.")
        
        w = obs.current
        
        # location details
        loc_str = loc.raw['address']['formattedAddress']

        # time details
        tz = pytz.timezone(obs.timezone)
        time = datetime.datetime.fromtimestamp(int(w.reference_time()), tz)
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
        
        await ctx.send(f">>> {loc_str} | {temp}°C {status_emoji}\n"
                        f"Feels like: {feels_like}°C | "
                        f"Humidity: {humidity}% | "
                        f"Wind: {wind_speed} km/h {wind_dir}\n"
                        f"Clouds: {cloud_cover}% | UV: {uv} | "
                        f"Visibility: {visibility} km\n"
                        f"Dew point: {dew_point}°C | "
                        f"Pressure: {pressure} kPa\n"
                        f"Last updated: {time_str} "
                        f"({obs.timezone})")

    @commands.command()
    async def forecast(self, ctx, *, place="Toronto, ON"):
        pass

def setup(bot):
    bot.add_cog(Weather(bot))
