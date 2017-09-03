import os
#import forecastiopy
import geocoder
import json
import discord

from forecastiopy import *
from pprint import pprint
from darksky import forecast
from discord.ext import commands
from utils.sharding import darkskyapi

api_key = darkskyapi

class Weather():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def weather(self, ctx, *, address: str):
        """Dark Sky Weather Results"""
        if ctx.message.author == ctx.message.author: #filler
            try:
                g = geocoder.google(address)
                results = g.latlng
                loc = g.address
                if "USA" in address:
                    fio = ForecastIO.ForecastIO(api_key, latitude=results[0], longitude=results[1], units=ForecastIO.ForecastIO.UNITS_US)
                else:
                    #for y'all celcius folks
                    fio = ForecastIO.ForecastIO(api_key, latitude=results[0], longitude=results[1])
                current = FIOCurrently.FIOCurrently(fio)
                alerts = FIOAlerts.FIOAlerts(fio)
                ds = forecast(api_key, results[0], results[1])
                if "USA" in address:
                    em = discord.Embed(description="This information is displayed in Farenheit.")
                else:
                    em = discord.Embed(description="This information is displayed in Celcius.")
                em.title = "{}'s Current Weather".format(loc)
                if current.uvIndex == 0:
                    uvresult = "There probably isn't any sun right now."
                    uvint = "0"
                elif current.uvIndex == range(1, 5):
                    uvresult = "Few sun rays are hitting."
                    uvint = current.uvIndex
                elif current.uvIndex == range(5, 8):
                    uvresult = "Hm.. The sun might be a bit stronk. Wear sunscreen if you're going out."
                    uvint = current.uvIndex
                elif current.uvIndex == range(8, 15):
                    uvresult = "Damn, the sun rays are hitting good here! Wear sunscreen definitely!"
                    uvint = current.uvIndex
                else:
                    uvresult = "Not available."
                    uvint = "N/A"
                try:
                    visib = current.visibility
                except AttributeError:
                    visib = "N/A"
                if ctx.message.server.me.color == None:
                	maybe = None
                else:
                	maybe = ctx.message.server.me.color
                try:
                    counties = ', '.join(ds.alerts[0].regions)
                    alertresult = "{} in {}. More info [at NWS]({} 'National Weather Service')".format(ds.alerts[0].title, counties, ds.alerts[0].uri)
                except AttributeError:
                    alertresult = "Not available."
                em.set_thumbnail(url="https://dragonfire.me/474be77b-23bc-42e4-a779-6eb7b3b9a892.jpg")
                em.color = maybe
                if "USA" in address:
                    em.add_field(name='Temperature', value="{}°F".format(current.temperature), inline=True)
                else:
                    em.add_field(name='Temperature', value="{}°C".format(current.temperature), inline=True)
                em.add_field(name='Currently', value="{}".format(current.summary), inline=True)
                em.add_field(name='Humidity', value="{:.0%}".format(current.humidity), inline=True)
                #this is a bit tricky when it comes to some countries so i'll leave it as is
                em.add_field(name='Wind Speed/Wind Gust', value="{} mph/{} mph".format(current.windSpeed, current.windGust), inline=True)
                #same for this
                em.add_field(name='Visibility', value="{} miles".format(visib), inline=True)
                em.add_field(name='UV Index', value="{} Current index is **{}**.".format(uvresult, uvint), inline=True)
                if fio.has_alerts() is True:
                    em.add_field(name='Weather Alert', value=alertresult, inline=True)
                await self.bot.say(embed=em)
            except Exception as fucking_hell:
                await self.bot.say("```py\n{}\n```".format(fucking_hell))
        else:
            await self.bot.say("Location isn't found or the given zip code or address is too short. Try again.")

    @commands.command(pass_context=True)
    async def locate(self, ctx, *, address: str):
        """Go fucking stalk someone"""
        try:
            g = geocoder.google(address)
            loc = g.json
            var = json.dumps(loc)
            k = json.loads(var)
            if k['status'] == 'OK':
            	yes = k['address']
            elif k['status'] == 'ZERO_RESULTS':
            	yes = "There's no results found for this location."
            await self.bot.say(yes)
        except Exception as e:
            await self.bot.say("```py\n{}\n```".format(e))

def setup(bot):
    bot.add_cog(Weather(bot))
