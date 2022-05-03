import discord
from discord.ext import commands

import os
import traceback
from datetime import datetime
import pytz

from dotenv import load_dotenv
load_dotenv()

from Ept import *
from trade import *

class trade_commands(commands.Cog):
    def __init__(self, bot, debug=False):
        self.bot = bot
        self.debug = debug or bool(os.getenv('DEBUG'))
        if self.debug:
            print("[LOG] Debugger Messages are ENABLED for [COG]: trade_cog")
    
    @commands.command(
        name    = 'trade',
        aliases = ['trad','tra','tr','t']
    )
    async def trade_command(self, ctx, ticker=None):
        """
        Called to initiate a transaction based on a ticker given
        
        Expected Behaviour:
        -----
        - Verifies integrity and type of parameters given
        - Queries stock-quote using backend method getquote()
        - Retrieves data by evaluating quote["priceFrom"]
        - Sends embed message with information about the stock based on the ticker given
        - Adds reactions for further instructing transactions (invokes buy_command, sell_command)

        Handled Exceptions:
        -----
        - [LOG]         Ept\TickerNotExistException
        - [LOG]         Ept\TickerNotSupportedException
        - [WARNING]     Ept\ConnectionError
        - (Exception)   
        """

        # parameter integrity and type-checking
        if not isinstance(ticker, str) or ticker.isdigit():
            await ctx.reply("**Error** | I don't know what you'd like to trade... :warning:\n"+\
                            "```\n{0}trade <ticker>\n```".format(os.getenv('PREFIX')))
            return
        
        try:
            # backend connection (invokes getquote)
            quote = getquote(ticker)

            # handle variables
            if quote["priceFrom"] == "pre":
                currentChange        = round(float(quote["preMarketChange"]),2)
                currentChangePercent = round(float(quote["preMarketChangePercent"]),2)
                price_msg            = "Pre-Market"
            elif quote["priceFrom"] == "reg":
                currentChange        = round(float(quote["regularMarketChange"]),2)
                currentChangePercent = round(float(quote["regularMarketChangePercent"]),2)
            elif quote["priceFrom"] == "post":
                currentChange        = round(float(quote["postMarketChange"]),2)
                currentChangePercent = round(float(quote["postMarketChangePercent"]),2)
                price_msg            = "Post-Market"
            else:
                raise ValueError("ValueError: quote[\"priceFrom\"] invalid")

            if currentChange > 0:
                change_msg = "```diff\n+{0} (+{1}%)\n```".format(currentChange,currentChangePercent)
            else:
                change_msg = "```diff\n{0} ({1}%)\n```".format(currentChange,currentChangePercent)

        except TickerNotExistException as e:
            print("[LOG] trade_command failed")
            print("[LOG]", e)
            await ctx.reply("**Error** | Your request could not be processed!\n"+\
                            "```\nThe ticker you have provided was not found\n```")
        
        except TickerNotSupportedException as e:
            print("[LOG] trade_command failed")
            print("[LOG]", e)
            await ctx.reply("**Error** | Your request could not be processed!\n"+\
                            "```\nThe ticker you have provided is not yet supported by Discord Trader\n```")

        except ConnectionError as e:
            print("[WARNING] trade_command failed")
            print("[WARNING]", e)
            await ctx.reply("**Error** | I was unable to process your request! :warning:\n"+\
                            "```\nConnection Timeout: Please try again later\n```")
        
        except Exception as e:
            print("[?????] trade_command failed")
            print("[?????]", traceback.format_exc())
            await ctx.reply("**Error** | Your request could not be processed! :warning:\n"+\
                            "```\nUnknown Exception: [{0}]\n```".format(e))

        else:
            # craft embed
            embed_descript = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"\
                +"\nYou are making a trade for [{0}](https://finance.yahoo.com/quote/{0}). ".format(quote["symbol"])\
                +"Please note that the quote provided may fluctuate and shall be used for reference only."\
                +"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            embed = discord.Embed(
                title       = "{0}".format(quote["shortName"]),
                description = embed_descript,
                colour      = discord.Colour.from_rgb(0,0,0)
            )
            # embed.set_author(
            #     name = ctx.author.display_name,
            #     icon_url = ctx.author.avatar_url
            # )
            embed.add_field(
                name        = "Price",
                value       = "```${0}```".format(quote["regularMarketPrice"]),
                inline      = True
            )
            
            # UI cases
            if quote["priceFrom"] == "reg":
                embed.add_field(
                    name    = "Trend",
                    value   = change_msg,
                    inline  = True
                )
            else:
                embed.add_field(
                    name    = price_msg,
                    value   = "```${0}```".format(quote["currentPrice"]),
                    inline  = True
                )
                embed.add_field(
                    name    = "Trend",
                    value   = change_msg,
                    inline  = True
                )
            
            # attempt to set company logo as embed thumbnail
            # by retrieving the logo from clearbit.com using the display_name or the ticker
            try:
                embed.set_thumbnail(
                    url = "https://logo.clearbit.com/{0}.com".format(quote["displayName"])
                )
                await ctx.channel.send(embed=embed)  
            except:
                try:
                    embed.set_thumbnail(
                        url = "https://logo.clearbit.com/{0}.com".format(quote["symbol"])
                    )
                    await ctx.channel.send(embed=embed)
                except:
                    await ctx.channel.send(embed=embed)
    
    @commands.command(
        name    = 'buy',
        aliases = ['b','+']
    )
    async def buy_command(self, ctx, ticker=None, quantity=None):
        """
        Called or invoked to complete a buy transaction based on a ticker given

        Expected Behaviour:
        -----
        - Verifies integrity and type of parameters given
        - Instructs buy transaction by invoking backend method buy()
        - Sends embed message with information about the transaction made

        Handled Exceptions:
        -----
        - [LOG]         Ept\MemberNotExistException
        - [LOG]         Ept\TickerNotExistException
        - [LOG]         Ept\TickerNotSupportedException
        - [LOG]         Ept\InsufficientBalanceException
        - [WARNING]     Ept\ConnectionError
        - (Exception)   
        """

        # parameter integrity and type-checking
        try:
            ticker = str(ticker)
            quantity = int(quantity)
            assert quantity > 0
        except Exception as e:
            print("[LOG] buy_command failed")
            print("[LOG]", e)
            await ctx.reply("**Error** | Your instruction could not be processed! :warning:\n"+\
                            "```\n{0}buy <ticker> <quantity>\n```".format(os.getenv('PREFIX')))
            return

        try:
            # backend connection (invokes getquote)
            quote = buy(ctx.author.id, ctx.author.guild.id, ticker, quantity)
           
            # handle variables
            quoteTime_conv = datetime.fromtimestamp(quote["currentTime"],pytz.timezone('US/Eastern'))

        except MemberNotExistException as e:
            print("[LOG] buy_command failed")
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

        except TickerNotExistException as e:
            print("[LOG] buy_command failed")
            print("[LOG]", e)
            await ctx.reply("**Error** | Your request could not be processed!\n"+\
                            "```\nThe ticker you have provided was not found\n```")
        
        except TickerNotSupportedException as e:
            print("[LOG] buy_command failed")
            print("[LOG]", e)
            await ctx.reply("**Error** | Your request could not be processed!\n"+\
                            "```\nThe ticker you have provided is not yet supported by Discord Trader\n```")

        except InsufficientBalanceException as e:
            print("[LOG] buy_command failed")
            print("[LOG]", e)
            await ctx.reply("**Error** | Your instruction has been declined! :no_entry_sign:\n"+\
                            "```\nInsufficient Balance\n```")

        except ConnectionError as e:
            print("[WARNING] buy_command failed")
            print("[WARNING]", e)
            await ctx.reply("**Error** | I was unable to process your request! :warning:\n"+\
                            "```\nConnection Timeout: Please try again later\n```")
        
        except Exception as e:
            print("[?????] buy_command failed")
            print("[?????]", traceback.format_exc())
            await ctx.reply("**Error** | Your request could not be processed! :warning:\n"+\
                            "```\nUnknown Exception: [{0}]\n```".format(e))
        
        else:
            # craft embed
            if quantity == 1:
                msg = "stock"
            else:
                msg = "stocks"

            embed = discord.Embed(
                title       = "Your instruction has been received! :white_check_mark:",
                description = "You have sucessfully purchased **{0}** **{1}** {2} for **${3}**."\
                    .format(quantity, quote["shortName"], msg, quote["currentPrice"]),
                timestamp   = quoteTime_conv,
                colour      = discord.Colour.from_rgb(0,0,0)
            )
            embed.add_field(
                name        = "\u200b",
                value       = "```diff\n+[{0}]{1}@{2}({3})\n```\n\u200b"\
                    .format(quantity,quote["symbol"],quote["currentPrice"],quoteTime_conv)
            )
            embed.set_footer(
                text        = "Discord Trader"
            )
            embed.set_author(
                name        = ctx.author.display_name,
                icon_url    = ctx.author.avatar_url
            )
            
            # output
            await ctx.channel.send(embed=embed)
    
    @commands.command(
        name    = 'sell',
        aliases = ['s','-']
    )
    async def sell_command(self, ctx, ticker=None, quantity=None):
        """
        Called or invoked to complete a sell transaction based on a ticker given

        Expected Behaviour:
        -----
        - Verifies integrity and type of parameters given
        - Instructs sell transaction by invoking backend method sell()
        - Sends embed message with information about the transaction made

        Handled Exceptions:
        -----
        - [LOG]         Ept\MemberNotExistException
        - [LOG]         Ept\TickerNotExistException
        - [LOG]         Ept\TickerNotSupportedException
        - [LOG]         Ept\InsufficientBalanceException
        - [WARNING]     Ept\ConnectionError
        - (Exception)   
        """

        try:
            ticker = str(ticker)
            quantity = int(quantity)
            assert quantity > 0
        except Exception as e:
            print("[LOG] sell_command failed")
            print("[LOG]", e)
            await ctx.reply("**Error** | Your instruction could not be processed! :warning:\n"+\
                            "```\n{0}sell <ticker> <quantity>\n```".format(os.getenv('PREFIX')))
            return

        try:
            # backend connection (invokes getquote)
            quote = sell(ctx.author.id, ctx.author.guild.id, ticker, quantity)
           
            # handle variables
            quoteTime_conv = datetime.fromtimestamp(quote["currentTime"],pytz.timezone('US/Eastern'))

        except MemberNotExistException as e:
            print("[LOG] sell_command failed")
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

        except TickerNotExistException as e:
            print("[LOG] sell_command failed")
            print("[LOG]", e)
            await ctx.reply("**Error** | Your request could not be processed!\n"+\
                            "```\nThe ticker you have provided was not found\n```")
        
        except TickerNotSupportedException as e:
            print("[LOG] sell_command failed")
            print("[LOG]", e)
            await ctx.reply("**Error** | Your request could not be processed!\n"+\
                            "```\nThe ticker you have provided is not yet supported by Discord Trader\n```")

        except InsufficientBalanceException as e:
            print("[LOG] sell_command failed")
            print("[LOG]", e)
            await ctx.reply("**Error** | Your instruction has been declined! :no_entry_sign:\n"+\
                            "```\nInsufficient Balance\n```")

        except ConnectionError as e:
            print("[WARNING] sell_command failed")
            print("[WARNING]", e)
            await ctx.reply("**Error** | I was unable to process your request! :warning:\n"+\
                            "```\nConnection Timeout: Please try again later\n```")
        
        except Exception as e:
            print("[?????] sell_command failed")
            print("[?????]", traceback.format_exc())
            await ctx.reply("**Error** | Your request could not be processed! :warning:\n"+\
                            "```\nUnknown Exception: [{0}]\n```".format(e))
        
        else:
            # craft embed
            if quantity == 1:
                msg = "stock"
            else:
                msg = "stocks"

            embed = discord.Embed(
                title       = "Your instruction has been received! :white_check_mark:",
                description = "You have sucessfully purchased **{0}** **{1}** {2} for **${3}**."\
                    .format(quantity, quote["shortName"], msg, quote["currentPrice"]),
                timestamp   = quoteTime_conv,
                colour      = discord.Colour.from_rgb(0,0,0)
            )
            embed.add_field(
                name        = "\u200b",
                value       = "```diff\n-[{0}]{1}@{2}({3})\n```\n\u200b"\
                    .format(quantity,quote["symbol"],quote["currentPrice"],quoteTime_conv)
            )
            embed.set_footer(
                text        = "Discord Trader"
            )
            embed.set_author(
                name        = ctx.author.display_name,
                icon_url    = ctx.author.avatar_url
            )
            
            # output
            await ctx.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(trade_commands(bot, debug=False))

print("[COG] Loaded trade cog")
