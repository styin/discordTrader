import discord
from discord.ext import commands

import os
import traceback
from disputils import BotEmbedPaginator

from dotenv import load_dotenv
load_dotenv()

from trade import *

class member_commands(commands.Cog):
    def __init__(self, bot, debug=False):
        self.bot = bot
        self.debug = debug or bool(os.getenv('DEBUG'))
        if self.debug:
            print("[LOG] Debugger Messages are ENABLED for [COG]: member_cog")
    
    @commands.command(
        name = 'start'
    )
    async def start_command(self, ctx):
        """
        Called to open up an account
        
        Expected Behaviour:
        -----
        - Invokes backend method start()
        - Sends embed message as response

        Handled Exceptions:
        -----
        - None
        """

        try:
            success = start(ctx.author.id, ctx.author.guild.id)
        
        except Exception as e:
            print("[?????] trade_command failed")
            print("[?????]", traceback.format_exc())
            await ctx.reply("**Error** | Your request could not be processed! :warning:\n"+\
                            "```\nUnknown Exception: [{0}]\n```".format(e))

        else:
            if success:
                # craft embed (success message)
                first_embed = discord.Embed(
                    title       = "Welcome to Discord Trader", 
                    description = "You have successfully initiated an account! :sparkles:\n\u200b",
                    colour      = discord.Colour.from_rgb(0,0,0)
                )
                first_embed.set_author(
                    name        = ctx.author.display_name,
                    icon_url    = ctx.author.avatar_url
                )
                first_embed.set_thumbnail(
                    url         = "https://cdn.discordapp.com/attachments/926858763389005824/928180562508783706/3052444-200.png"
                )
                first_embed.add_field(
                    name        = "Getting Started",
                    value       = "Before you set off and begin making a fortune, note that your initial balance is set to be `$100,000.00`.",
                    inline      = False
                )
                first_embed.add_field(
                    name        = "\u200b",
                    value       = "Now, when you're ready, use `{0}trade <ticker>` to start trading a stock, or use `{0}buy <ticker> <quantity>`, `{0}sell <ticker> <quantity>` for direct transactions."\
                        .format(os.getenv('PREFIX')),
                    inline      = False
                )
                first_embed.add_field(
                    name        = "\u200b",
                    value       = "If you get stuck, use `{0}help` for some advice, and in case you do not know what *tickers* are, use `{0}ticker` for some references.\n\u200b"\
                        .format(os.getenv('PREFIX'))
                )

                # craft embed (disclaimer)
                second_embed = discord.Embed(
                    title       = "Notice",
                    description = "Discord Trader was created to simulate stock-trading for the sole purpose of education and entertainment. Investors of the real market are advised to conduct their own independent research into individual stocks before making a purchase decision.",
                    colour      = discord.Colour.from_rgb(112,41,99)
                )

                # output
                await ctx.send(embed=first_embed)
                await ctx.send(embed=second_embed)
            else:
                # craft embed
                embed = discord.Embed(
                    title       = "Hi there~ Looks like you already have an account!",
                    description = "It'd be kind of unfair, if you had multiple ones on this server...".format(os.getenv('PREFIX')),
                    colour      = discord.Colour.from_rgb(0,0,0)
                )
                embed.set_author(
                    name        = ctx.author.display_name,
                    icon_url    = ctx.author.avatar_url
                )
                
                # output
                await ctx.channel.send(embed=embed)
    
    @commands.command(
        name    = 'balance',
        aliases = ['bal','$']
    )
    async def balance_command(self, ctx):
        """
        Called to inquire account balance

        Expected Behaviour:
        -----
        - Invokes backend method getbalance()
        - Send embed message with balance information

        Handled Exceptions:
        -----
        - [LOG]     Ept\MemberNotExistException
        - (Exception)
        """

        try:
            # backend connection (invokes getbalance)
            balance = getbalance(ctx.author.id, ctx.author.guild.id)

        except MemberNotExistException as e:
            print("[LOG] balance_command failed")
            print("[LOG]", e)
            embed = discord.Embed(
                title = "Hi there! Have you opened your account yet?",
                description = "Use **{0}start** to get started~ :sparkles:".format(os.getenv('PREFIX')),
                colour      = discord.Colour.from_rgb(0,0,0)
            )
            embed.set_author(
                name        = ctx.author.display_name,
                icon_url    = ctx.author.avatar_url
            )
            await ctx.reply(embed=embed)

        except Exception as e:
            print("[?????] balance_command failed")
            print("[?????]", traceback.format_exc())
            await ctx.reply("**Error** | Your request could not be processed! :warning:\n"+\
                            "```\nUnknown Exception: [{0}]\n```".format(e))
            return

        else:
            # craft embed
            embed = discord.Embed(
                title = "Here is your current balance. :moneybag:",
                description = "```\n${0}\n```".format(balance),
                colour      = discord.Colour.from_rgb(0,0,0)
            )
            embed.set_footer(
                text = "Discord Trader"
            )
            embed.set_author(
                name = ctx.author.display_name,
                icon_url = ctx.author.avatar_url
            )

            # output
            await ctx.channel.send(embed=embed)

    @commands.command(
        name = 'daily'
    )
    async def daily_command(self, ctx):
        """
        Called to receive a daily monetary reward

        Expected Behaviour:
        -----
        - Invokes backend method addmoney()
        - Sends embed message with information about the receival of the reward
        
        Handled Exception:
        -----
        - [LOG]     Ept\MemberNotExistException
        - (Exception)
        """

        try:
            # backend connection (invokes addmoney)
            result = addmoney(ctx.author.id, ctx.author.guild.id)

            # handle variables
            timeLeft = int(result.get("timeLeft",None)/60)
            hoursLeft = int(timeLeft/60)
            minutesLeft = int(timeLeft%60)

            amountAdded = round(result.get("amountAdded",0),2)
            newBalance = result.get("Balance",None)

        except MemberNotExistException as e:
            print("[LOG] daily_command failed")
            print("[LOG]", e)
            embed = discord.Embed(
                title = "Hi there! Have you opened your account yet?",
                description = "Use `{0}start` to get started~ :sparkles:".format(os.getenv('PREFIX')),
                colour      = discord.Colour.from_rgb(0,0,0)
            )
            embed.set_author(
                name        = ctx.author.display_name,
                icon_url    = ctx.author.avatar_url
            )
            await ctx.reply(embed=embed)

        except Exception as e:
            print("[?????] daily_command failed")
            print("[?????]", traceback.format_exc())
            await ctx.reply("**Error** | Your request could not be processed! :warning:\n"+\
                            "```\nUnknown Exception: [{0}]\n```".format(e))
        
        else:
            if result.get("Success") == True:
                embed = discord.Embed(
                    title       = "Success. You have claimed your daily reward: ${0}! :sparkles:".format(amountAdded),
                    description = "Your new balance is:\n```\n${0}\n```\nClaim your next reward in `{1}h{2}min`".format(newBalance, hoursLeft, minutesLeft),
                    colour      = discord.Colour.from_rgb(0,0,0)
                )
                embed.set_author(
                    name        = ctx.author.display_name,
                    icon_url    = ctx.author.avatar_url
                )
                await ctx.channel.send(embed=embed)
            
            elif result.get("Success") == False:
                embed = discord.Embed(
                    title       = "Sorry, but it looks like your daily reward isn't available yet. :no_entry_sign:",
                    description = "Try again in `{0}h{1}min`...".format(hoursLeft, minutesLeft),
                    colour      = discord.Colour.from_rgb(0,0,0)
                )
                embed.set_author(
                    name        = ctx.author.display_name,
                    icon_url    = ctx.author.avatar_url
                )
                await ctx.reply(embed=embed)

    @commands.command(
        name = 'holdings',
        aliases = ['h','hold']
    )
    async def holdings_command(self, ctx):
        """
        Called to inquiry account holdings
        
        Expected Behaviour:
        -----
        - Retrieves holdings data by invoking backend method holdings()
        - Sends embed message with holdings information
        - Adds reactions for pagination

        Handled Exceptions:
        ---
        - [LOG]     Ept\MemberNotExistException
        - [LOG]     Ept\InsufficientHoldingsException
        - (Exception)
        """
        try:
            # backend connection (invokes holdings)
            holdings_list = holdings(ctx.author.id, ctx.author.guild.id)

            # handle pages of holdings
            holdings_pages = []
            for stocks in holdings_list:
                
                #temporary
                companyName = getquote(stocks[0]).get('shortName','-/-')
                    
                shares          = stocks[1]
                averageCost     = stocks[2]
                currentPrice    = stocks[3]
                holdingReturn   = round(stocks[4],2)
                holdingChange   = round(stocks[5]*100,2)
                holdingValue    = currentPrice * shares

                if holdingReturn > 0:
                    holdingReturn_msg = "```diff\n+{0} (+{1}%)\n```".format(holdingReturn, holdingChange)
                else:
                    holdingReturn_msg = "```diff\n{0} ({1}%)\n```".format(holdingReturn, holdingChange)
                
                embed = discord.Embed(
                    title       = "Here are your current holdings.",
                    description = "\n\u200b",
                    colour      = discord.Colour.from_rgb(0,0,0)
                )
                embed.set_author(
                    name        = ctx.author.display_name,
                    icon_url    = ctx.author.avatar_url
                )
                embed.add_field(
                    name        = "{0} [{1}]".format(companyName,stocks[0]),
                    value       = str("━━━━━━━━━━━━━━━━━━━━━━━━━\n"\
                                + "shares: `{0}`\n".format(shares)\
                                + "average cost/share: `${0}`\n".format(averageCost)\
                                + "current price: `${0}`\n".format(currentPrice)\
                                + "holding value: `${0}`\n".format(holdingValue)\
                                + "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                + "return (% change): \n{0}\n\u200b".format(holdingReturn_msg)
                    )
                )
                holdings_pages.append(embed)

        except MemberNotExistException as e:
            print("[LOG] holdings_command failed")
            print("[LOG]", e)
            embed = discord.Embed(
                title = "Hi there! Have you opened your account yet?",
                description = "Use `{0}start` to get started~ :sparkles:".format(os.getenv('PREFIX')),
                colour      = discord.Colour.from_rgb(0,0,0)
            )
            embed.set_author(
                name        = ctx.author.display_name,
                icon_url    = ctx.author.avatar_url
            )
            await ctx.reply(embed=embed)

        except InsufficientHoldingsException as e:
            print("[LOG] holdings_command failed")
            print("[LOG]", e)
            embed = discord.Embed(
                title = "You currently do not have any holdings.",
                description = "Try using `{0}buy` or `{0}trade` to invest in some stocks to get started~".format(os.getenv('PREFIX')),
                colour      = discord.Colour.from_rgb(0,0,0)
            )
            embed.set_author(
                name        = ctx.author.display_name,
                icon_url    = ctx.author.avatar_url
            )
            await ctx.channel.send(embed=embed)

        except Exception as e:
            print("[?????] buy_command failed")
            print("[?????]", traceback.format_exc())
            await ctx.reply("**Error** | Your request could not be processed! :warning:\n"+\
                            "```\nUnknown Exception: [{0}]\n```".format(e))

        else:   
            paginator = BotEmbedPaginator(ctx, holdings_pages)
            await paginator.run(timeout=30)

def setup(bot):
    bot.add_cog(member_commands(bot, debug=False))

print("[COG] Loaded member cog")
