import os
import sys
import json
import aiohttp
import asyncio

from main import owner_id
from config.config import Config

import discord
from discord.ext.commands import bot
from discord.ext.commands import group


def owner(ctx):
	return owner_id == ctx.message.author.id

# TODO: Clean the fuck up
class Settings():
	def __init__(self, Bot):
		self.bot = Bot
		self.con = Config(Bot)
		self.serverconfig = self.con.serverconfig

	@bot.command(pass_context=True, hidden=True)
	async def blacklist(self, ctx, option, *args):
		"""
		Usage:
			.blacklist [ + | - | add | remove ] @UserName [@UserName2 ...]

		Add or remove users to the blacklist.
		Blacklisted users are forbidden from using bot commands.
		Only the bot owner can use this command
		"""
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		blacklist_amount = 0
		mentions = ctx.message.mentions

		if not mentions:
			return await self.bot.say("You didn't mention anyone")

		if option not in ['+', '-', 'add', 'remove']:
			return await self.bot.say('Invalid option "%s" specified, use +, -, add, or remove' % option, expire_in=20)

		for user in mentions:
			if user.id == owner_id:
				print("[Commands:Blacklist] The owner cannot be blacklisted.")
				await self.bot.say("The owner cannot be blacklisted.")
				mentions.remove(user)

		if option in ['+', 'add']:
			with open("config/blacklist.txt", "r") as fp:
				for user in mentions:
					for line in fp.readlines():
						if user.id + "\n" in line:
							mentions.remove(user)

			with open("config/blacklist.txt", "a+") as fp:
				lines = fp.readlines()
				for user in mentions:
					if user.id not in lines:
						fp.write("{}\n".format(user.id))
						blacklist_amount += 1
			return await self.bot.say('{} user(s) have been added to the blacklist'.format(blacklist_amount))

		elif option in ['-', 'remove']:
			with open("config/blacklist.txt", "r") as fp:
				lines = fp.readlines()
			with open("config/blacklist.txt", "w") as fp:
				for user in mentions:
					for line in lines:
						if user.id + "\n" != line:
							fp.write(line)
						else:
							fp.write("")
							blacklist_amount += 1
				return await self.bot.say('{} user(s) have been removed from the blacklist'.format(blacklist_amount))


	@bot.command(pass_context=True, hidden=True)
	async def enablesetting(self, ctx, setting):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		else:
			server_id = ctx.message.server.id
			if setting in self.serverconfig[server_id]:
				self.serverconfig = self.con.load_config()
				if not self.serverconfig[server_id][setting]["enabled"]:
					self.serverconfig[server_id][setting]["enabled"] = 1
					self.con.updateconfig(self.serverconfig)
					return await self.bot.say("'{}' was enabled!".format(setting))
				else:
					self.serverconfig[server_id][setting]["enabled"] = 0
					self.con.updateconfig(self.serverconfig)
					return await self.bot.say("'{}' was disabled :cry:".format(setting))
			else:
				return await self.bot.say("That module dont exist fam. You made the thing")

	@bot.command(pass_context=True)
	async def printsettings(self, ctx, setting=None):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		else:
			self.serverconfig = self.con.load_config()
			config = self.serverconfig[ctx.message.server.id]
			if setting in config:
				config = config[setting]
			return await self.bot.say(str(json.dumps(config, indent=4)))

	@group(pass_context=True, hidden=True)
	async def set(self, ctx):
		if ctx.invoked_subcommand is None:
			return await self.bot.say('Missing Argument')

	@set.command(pass_context=True, hidden=True)
	async def welcomechannel(self, ctx, channel: discord.Channel = None):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		else:
			self.serverconfig = self.con.load_config()
			self.serverconfig[ctx.message.server.id]["greets"]["welcome-channel"] = channel.id
			self.con.updateconfig(self.serverconfig)
		return await self.bot.say("{} has been set as the welcome channel!".format(channel.mention))

	@set.command(pass_context=True, hidden=True)
	async def goodbyechannel(self, ctx, channel: discord.Channel = None):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		else:
			self.serverconfig = self.con.load_config()
			self.serverconfig[ctx.message.server.id]["goodbyes"]["goodbye-channel"] = channel.id
			self.con.updateconfig(self.serverconfig)
		return await self.bot.say("{} has been set as the goodbye channel!".format(channel.mention))

	@set.command(pass_context=True, hidden=True)
	async def twitchchannel(self, ctx, channel: discord.Channel = None):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		else:
			self.serverconfig = self.con.load_config()
			self.serverconfig[ctx.message.server.id]["twitch"]["twitch-channel"] = channel.id
			self.con.updateconfig(self.serverconfig)
		return await self.bot.say("{} has been set as the twitch shilling channel!".format(channel.mention))

	@set.command(pass_context=True, hidden=True)
	async def welcomemessage(self, ctx, *, message: str):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		else:
			self.serverconfig = self.con.load_config()
			self.serverconfig[ctx.message.server.id]["greets"]["custom-message"] = message
			self.con.updateconfig(self.serverconfig)
		return await self.bot.say("Custom message set to '{}'".format(message))

	@set.command(pass_context=True, hidden=True)
	async def muterole(self, ctx, role: discord.Role = None):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		else:
			self.serverconfig = self.con.load_config()
			self.serverconfig[ctx.message.server.id]["mute"]["role"] = role.id
			self.con.updateconfig(self.serverconfig)
		return await self.bot.say("Muted role set to '{}'".format(role.name))

	@set.command(pass_context=True, hidden=True)
	async def muteadmin(self, ctx, role: discord.Role = None):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		else:
			self.serverconfig = self.con.load_config()
			self.serverconfig[ctx.message.server.id]["mute"]["admin-role"].append(role.id)
			self.con.updateconfig(self.serverconfig)
		return await self.bot.say("Admin role appended to list: '{}'".format(role.name))

	@bot.command(pass_context=True, hidden=True, aliases=["setava"])
	async def changeavatar(self, ctx, url=None):
		"""
		Usage:
			{command_prefix}setavatar [url]

		Changes the bot's avatar.
		Attaching a file and leaving the url parameter blank also works.
		"""
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)

		if ctx.message.attachments:
			thing = ctx.message.attachments[0]['url']
		else:
			thing = url.strip('<>')

		avaimg = 'avaimg.png'
		with aiohttp.ClientSession() as session:
			async with session.get(thing) as img:
				with open(avaimg, 'wb') as f:
					f.write(await img.read())
		with open(avaimg, 'rb') as f:
			await self.bot.edit_profile(avatar=f.read())
		os.remove(avaimg)
		asyncio.sleep(2)
		return await self.bot.say(":ok_hand:")

	@bot.command(pass_context=True, hidden=True, aliases=["nick"])
	async def changenickname(self, ctx, *nick):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		else:
			if ctx.message.channel.permissions_for(ctx.message.server.me).change_nickname:
				await self.bot.change_nickname(ctx.message.server.me, ' '.join(nick))
				return await self.bot.say(":thumbsup:")
			else:
				return await self.bot.say("I don't have permission to do that :sob:", delete_after=self.con.delete_after)

	@bot.command(pass_context=True, hidden=True, aliases=["setgame", "game"])
	async def changegame(self, ctx, *, game: str):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		else:
			if game.lower() == "none":
				game_name = None
			else:
				game_name = discord.Game(name=game)
			await self.bot.change_presence(game=game_name, afk=False)
			return await self.bot.say(":ok_hand: Game set to {}".format(str(game_name)))

	@bot.command(pass_context=True, hidden=True, aliases=["status"])
	async def changestatus(self, ctx, status: str):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		else:
			status = status.lower()
			if status == 'offline' or status == 'invisible':
				discordStatus = discord.Status.invisible
			elif status == 'idle':
				discordStatus = discord.Status.idle
			elif status == 'dnd':
				discordStatus = discord.Status.dnd
			else:
				discordStatus = discord.Status.online
			await self.bot.change_presence(status=discordStatus)
			await self.bot.say("**:ok:** Status set to {}".format(discordStatus))

	@bot.command(pass_context=True, hidden=True)
	async def echo(self, ctx, channel, *, message: str):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		else:
			if ctx.message.channel_mentions:
				for channel in ctx.message.channel_mentions:
					await self.bot.send_message(channel, content=message)
				return await self.bot.say(":point_left:")
			elif channel.isdigit():
				channel = ctx.message.server.get_channel(channel)
				await self.bot.send_message(channel, content=message)
				return await self.bot.say(":point_left:")
			else:
				return await self.bot.say("You did something wrong smh")

	@bot.command(pass_context=True, hidden=True)
	async def restart(self, ctx):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)

		await self.bot.logout()
		return os.execl(sys.executable, sys.executable, *sys.argv)

	@bot.command(pass_context=True, hidden=True)
	async def shutdown(self, ctx):
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)

		await self.bot.logout()
		return exit(0)

	@bot.command(pass_context=True, hidden=True)
	async def announce(self, ctx, *announcement):
		"""
		ONLY USE FOR SERIOUS ANNOUNCEMENTS
		"""
		if not owner(ctx):
			return await self.bot.reply(self.con.no_perms_reponse, delete_after=self.con.delete_after)
		else:
			# TODO: Make colour top level role colour
			# TODO: Custom message for annoucement footer
			embed = discord.Embed(title="RoxBot Announcement", colour=discord.Colour(0x306f99), description=' '.join(announcement))
			embed.set_footer(text="This message has be automatically generated by a cute ass Roxie",
							 icon_url=self.bot.user.avatar_url)
			for server in self.bot.servers:
				await self.bot.send_message(server, embed=embed)
			return await self.bot.say("Done!", delete_after=self.con.delete_after)


def setup(Bot):
	Bot.add_cog(Settings(Bot))
