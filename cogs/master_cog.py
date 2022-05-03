import discord
from discord.ext import commands

import os
from datetime import date, datetime

from dotenv import load_dotenv
load_dotenv()

class Master(commands.Cog):
    def __init__(self, bot, debug=False):
        self.bot = bot
        self.debug = debug or bool(os.getenv('DEBUG'))
        self._last_member = None
        if self.debug:
            print("[LOG] Debugger Messages are ENABLED for [COG]: master_cog")
    
    # Voice State Update Logger
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Detects Voice State Update"""
        if self.debug:
            print("[DEBUG] {0} ID:({1}) had a voice_state_update in {2}"\
            .format(member.display_name, member.id, after.channel))
    
    # Greetings and Information
    @commands.command(
        aliases=['hi','info']
    )
    async def hello(self, ctx, *, member: discord.Member = None):
        """This command returns some basic information"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            title_msg = "Hello {0.name}~ :sparkles:".format(member)
        else:
            title_msg = "Hello {0.name}... This feels familiar...".format(member)
        self._last_member = member
        # Crafting the message
        embed = discord.Embed(
            title       = title_msg,
            description = "I am **Discord Trader**, a bot who simulates stock-trading. :money_with_wings:\nUse **{0}start** to get started!\n"
                .format(os.getenv('PREFIX')),
            colour      = discord.Colour.from_rgb(0,0,0)
        )
        embed.add_field(
            name        = "prefix",
            value       = self.bot.command_prefix,
            inline      = True
        )
        embed.add_field(
            name        = "developed by",
            value       = "YZ-Discord API Dev Team",
            inline      = True
        )
        embed.add_field(
            name        = "version",
            value       = os.getenv('VERSION'),
            inline      = True
        )
        await ctx.channel.send(embed=embed)
    
    # Safe Logout
    @commands.command(
        aliases=['exit','quit','shutdown']
    )
    async def logout(self, ctx):
        """The Safe Logout Command"""
        if ctx.author.id == int(os.getenv('styID')) or ctx.author.id == int(os.getenv('nnID')):
            print("[LOG] Scheduled Shutdown Initiated")
            embed = discord.Embed(
                title       = "Safely shutting down... :white_check_mark:",
                description = "A scheduled shutdown has been initiated, and the Discord Trader Bot is logging off.",
                colour      = discord.Colour.from_rgb(0,0,0)
            )
            await ctx.reply(embed=embed)
            await self.bot.close()
        else:
            print("[LOG] Unauthorized Logout")
            embed = discord.Embed(
                title       = "Unauthorized Activity :lock:",
                description = "Insufficient Permissions! Please verify your clearance.",
                colour      = discord.Colour.from_rgb(0,0,0)
            )
            await ctx.reply(embed=embed)

    # Suggestions Relay
    @commands.command(
        aliases = ['bug']
    )
    async def suggest(self, ctx, *args):
        """Called to make a suggestion, which gets relayed to the suggestions box"""
        
        if args == ():
            await ctx.reply("**Error** | Please clarify your suggestion. :warning:\n"+\
                            "```\n{0}suggest <your message>\n```".format(os.getenv('PREFIX')))
            return
        
        channel         = self.bot.get_channel(int(os.getenv('suggestion_box_chID')))
        suggestion      = "{0}".format(' '.join(args))
        suggestionID    = int(datetime.timestamp(datetime.now()))

        reply_embed = discord.Embed(
            title = "Your message has been received! :sparkles:",
            description = "Thank you for your support. We will keep you updated on your suggestion here:\n{0.mention}".format(channel),
            colour = discord.Colour.from_rgb(0,0,0)
        )
        reply_embed.add_field(
            name = "\n\u200b",
            value = "```\n{0}\n```".format(suggestion)
        )
        reply_embed.set_author(
            name = ctx.author.display_name,
            icon_url = ctx.author.avatar_url
        )
        reply_embed.set_footer(
            text = suggestionID
        )

        suggestion_embed = discord.Embed(
            title = "Suggestion Number {0}".format(suggestionID),
            description = "```\n{0}\n```".format(suggestion),
            colour = discord.Colour.from_rgb(0,0,0)
        )
        
        await ctx.channel.send(embed=reply_embed)
        await channel.send(embed=suggestion_embed)

def setup(bot):
    bot.add_cog(Master(bot, debug=False))

print("[COG] Loaded master cog")
