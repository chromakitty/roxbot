
from overwatch_api.core import AsyncOWAPI
from overwatch_api.constants import *
import json
from discord.ext.commands import bot
import discord

class Overwatch():
    def __init__(self, Bot):
        self.bot = Bot
        self.client = AsyncOWAPI()

    @bot.command(pass_context=True)
    async def test(self, ctx, username: str):
        print(username)
        data = {}
        data["PC"] = await self.client.get_profile(username, platform=PC)
        print(data["PC"]['eu']['heroes']['playtime'])
        with open('overwatchdump.json', 'w') as over_file:
            json.dump(data["PC"], over_file)
        return await self.bot.say(str(data["PC"]['eu']['heroes']['playtime']))

def setup(Bot):
    Bot.add_cog(Overwatch(Bot))