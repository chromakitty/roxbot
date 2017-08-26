import random
import json
import os
import requests
import aiohttp
from libs.scrapper.scrapper import scrapper
from discord.ext.commands import bot


class Fun():
	def __init__(self, Bot):
		self.bot = Bot

	@bot.command(pass_context=True)
	async def roll(self, ctx, die):
		"""
		Rolls a die using ndx format.
		Usage:
			{command_prefix}roll ndx
		Example:
			.roll 2d20 # Rolls two D20s

		"""
		# TODO: Change to ndx format
		dice = 0
		if die[0].isdigit():
			if die[1].isdigit() or die[0] == 0:
				return await self.bot.say("I only support multipliers from 1-9")
			multiplier = int(die[0])
		else:
			multiplier = 1
		if die[1].lower() != "d" and die[0].lower() != "d":
			return await self.bot.say("Use the format 'ndx'.")
		options = (4, 6, 8, 10, 12, 20, 100)
		for option in options:
			if die.endswith(str(option)):
				dice = option
		if dice == 0:
			return await self.bot.say("You didn't give a die to use.")

		rolls = []
		if dice == 100:
			step = 10
		else:
			step = 1

		total = 0
		if multiplier > 1:
			for x in range(multiplier):
				rolls.append(random.randrange(step, dice+1, step))
			for r in rolls:
				total += r
			return await self.bot.say("{} rolled **{}**. Totaling **{}**".format(ctx.message.author.mention, rolls, total))
		else:
			roll = random.randrange(step, dice + 1, step)
			return await self.bot.say("{} rolled a **{}**".format(ctx.message.author.mention, roll))

	@bot.command(pass_context=True)
	async def suck(self, ctx):
		"""
		Sucks the mentioned user ;)
		Usage:
			{command_prefix}suck @user#9999
		"""
		if len(ctx.message.mentions) < 1:
			return await self.bot.say("You didn't mention someone for me to suck")
		user = ctx.message.mentions[0]
		return await self.bot.say(":eggplant: :sweat_drops: :tongue: {}".format(user.mention))

	@bot.command(pass_context=True, aliases=["wf"])
	async def waifurate(self, ctx):
		"""
		Rates the mentioned waifu(s)
		Usage:
			{command_prefix}waifurate @user#9999
		"""
		mentions = ctx.message.mentions
		if not mentions:
			return await self.bot.reply("You didn't mention anyone for me to rate.", delete_after=10)

		rating = random.randrange(1, 11)
		if rating <= 2:
			emoji = ":sob:"
		elif rating <= 4:
			emoji = ":disappointed:"
		elif rating <= 6:
			emoji = ":thinking:"
		elif rating <= 8:
			emoji = ":blush:"
		elif rating == 9:
			emoji = ":kissing_heart:"
		else:
			emoji = ":heart_eyes:"

		if len(mentions) > 1:
			return await self.bot.say("Oh poly waifu rating? :smirk: Your combined waifu rating is {}/10. {}".format(rating, emoji))
		else:
			return await self.bot.say("Oh that's your waifu? I rate them a {}/10. {}".format(rating, emoji))

	@bot.command(pass_context=True, aliases=["cf"])
	async def coinflip(self, ctx):
		"""Flip a coin"""
		return await self.bot.reply("the coin landed on {}!".format(random.choice(["heads", "tails"])))

	@bot.command(pass_context=True)
	async def aesthetics(self, ctx, *convert):
		"""Converts text to be more  a e s t h e t i c s"""
		WIDE_MAP = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))
		WIDE_MAP[0x20] = 0x3000
		convert = str(' '.join(convert)).translate(WIDE_MAP)
		return await self.bot.say(convert)

	@bot.command(pass_context=True)
	async def reddit(self, ctx, subreddit):
		links = scrapper().linkget(subreddit, True)
		if not links:
			return await self.bot.say("Error ;-; That subreddit probably doesn't exist. Please check your spelling")
		url = ""
		while not url:
			choice = random.choice(links)
			url = scrapper().retriveurl(choice["data"]["url"])

		if url.split("/")[-2] == "a":
			text = "This is an album, click on the link to see more. "
		else:
			text = ""
		return await self.bot.say(text + url)

	@bot.command()
	async def aww(self):
		links = scrapper().linkget("aww", True)
		if not links:
			return await self.bot.say("Error ;-; That subreddit probably doesn't exist. Please check your spelling")
		url = ""
		while not url:
			choice = random.choice(links)
			url = scrapper().retriveurl(choice["data"]["url"])

		if url.split("/")[-2] == "a":
			text = "This is an album, click on the link to see more. "
		else:
			text = ""
		return await self.bot.say(text + url)

	@bot.command(pass_context=True)
	async def upload(self, ctx):
		"""
		Uploads selected file to the host, thanks to the fact that
		every pomf.se based site has pretty much the same architecture.
		"""
		sites = [
			["https://comfy.moe/", 2147483648],
			["https://safe.moe/api/", 209715200],
			["http://up.che.moe/", 52428800],
			["https://mixtape.moe/", 104857600],
			["https://pomf.cat/", 78643200],
			["https://sugoi.vidyagam.es/", 104857600],
			["https://doko.moe/", 2147483648],
			["https://pomfe.co/", 104857600],
			["https://pomf.space/", 268435456],
			["https://vidga.me/", 104857600],
			["https://pomf.pyonpyon.moe/", 52428800]
		] # List of pomf clone sites and upload limits


		await self.bot.send_typing(ctx.message.channel)
		if ctx.message.attachments:
			urls = []
			for attachment in ctx.message.attachments:
				name = attachment['url'].split("/")[-1]
				# Download File
				with aiohttp.ClientSession() as session:
					async with session.get(attachment['url']) as img:
						with open(name, 'wb') as f:
							f.write(await img.read())
				# Site choice, shouldn't need an upload size check since max upload for discord atm is 50MB
				site = random.choice(sites)

				# Upload file
				try:
					with open(name, 'rb') as f:
						answer = requests.post(url=site+"upload.php",files={'files[]': f.read()})
						response = json.loads(answer.text)
						file_name_1 = response["files"][0]["url"].replace("\\", "")
					urls.append(file_name_1)
				except Exception as e:
					print(e)
					print(name + ' couldn\'t be uploaded to ' + site)
				os.remove(name)
			msg = "".join(urls)
			return await self.bot.say(msg)
		else:
			return await self.bot.say("Send me shit to upload nig")


def setup(Bot):
	Bot.add_cog(Fun(Bot))
