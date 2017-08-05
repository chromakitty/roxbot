from overwatch_api.core import AsyncOWAPI
from overwatch_api.constants import *
import json
from discord.ext.commands import bot
from discord.ext.commands import group
import discord

class Overwatch():
    def __init__(self, Bot):
        self.bot = Bot
        self.client = AsyncOWAPI()
        self.achievements_list = json.load(open('cogs/overwatch_achievements.json', 'r'))

    @group(pass_context=True, aliases=["ow"])
    async def overwatch(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid git command passed...')

    @overwatch.command(pass_context=True)
    async def test(self, ctx, username: str):
        print(username)
        data = {}
        data["PC"] = await self.client.get_profile(username, platform=PC)
        print(data["PC"]['eu']['heroes']['playtime'])
        with open('overwatchdump.json', 'w') as over_file:
            json.dump(data["PC"], over_file)
        return await self.bot.say(str(data["PC"]['eu']['heroes']['playtime']))

    @overwatch.command(pass_context=True)
    async def achievements(self, ctx, username:str):
        # TODO: Make it work for the whole set of achievements
        data = {}
        NotPassed = True
        while NotPassed:
            try:
                data["PC"] = await self.client.get_achievements(username, platform=PC)
                NotPassed = False
            except:
                pass
        value = ""
        num = 0
        for achievement in self.achievements_list["General"]:
            if data["PC"]["eu"]["general"][achievement]:
                emoji = ':white_check_mark: '
                num += 1
            else:
                emoji = ":x: "
            value = value + emoji + "**" + achievement.title().replace("_"," ") + "**: " + self.achievements_list["General"][achievement] + "\n"
        name = " " + str(num) + "/" + str(len(self.achievements_list["General"]))

        embed = discord.Embed(colour=discord.Colour(0xfaa02e), description="__**Achivements**__")
        embed.set_author(name="Roxxers#2827")
        embed.add_field(name="General:"+name, value=value, inline=False)

        return await self.bot.say(embed=embed)

def setup(Bot):
    Bot.add_cog(Overwatch(Bot))