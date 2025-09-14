import discord
from discord.ext import commands
import datetime
import traceback, sys

from cogs.checks import checks
from cache.cache import cache

import databases.ticket_settings
import databases.tickets
import databases.users
from services.logging import logger

from themes import color
from functions import pings
import asyncio

import json

from core.Bot import AutoShardedBot

import databases

import random

def get_formatted_balance(balance: int) -> str:
    # Format balance with suffixes like 1m, 1k, 1b with max 1 decimal if needed
    if balance >= 1_000_000_000:
        formatted = balance / 1_000_000_000
        suffix = "b"
    elif balance >= 1_000_000:
        formatted = balance / 1_000_000
        suffix = "m"
    elif balance >= 1_000:
        formatted = balance / 1_000
        suffix = "k"
    else:
        return str(balance)
    
    # Check if the decimal part is zero
    if formatted.is_integer():
        return f"{int(formatted)}{suffix}"
    else:
        return f"{formatted:.1f}{suffix}"

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot:AutoShardedBot = bot
        class cog_info:
            name =  "Economy"
            category = "Extra"
            description =  "Economy commands"
            hidden =  False
            emoji = self.bot.emoji.TICKET
        self.cog_info = cog_info


    def check_economy_rules_predicate(self,ctx):
        try:
            economy_rules_accepted = cache.users.get(str(ctx.author.id),{}).get("economy_rules_accepted",False)
            if economy_rules_accepted:
                return True
            return False
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
            return False
    



    accept_economy_message_sended = {} # {user_id:datetime.datetime} will send the message every 5 minutes timeout
    async def accept_economy_rules(self,ctx:commands.Context):
        try:
            if self.check_economy_rules_predicate(ctx):
                return True
            if ctx.author.id in self.accept_economy_message_sended:
                if self.accept_economy_message_sended[ctx.author.id] + datetime.timedelta(minutes=5) > datetime.datetime.now():
                    return False
            self.accept_economy_message_sended[ctx.author.id] = datetime.datetime.now()
            embed = discord.Embed(
                title="Economy Rules",
                description=f"""**{ctx.author.mention} | To Use Economy Commands You Must Accept The Economy Rules

1. Economy Assets Can't be used to buy real world items
2. Economy Assets Can't be sold for real world money
3. Economy Assets Can't be used to Exchange for Something except for the Bot Shop Items Like Premium & More
**""",
                color=color.red
            )
            embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.display_avatar.url,url=self.bot.urls.TERMS_OF_SERVICE)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_footer(text="Required to use economy commands",icon_url=self.bot.user.display_avatar.url)
            view = discord.ui.View(timeout=600)
            accept_button = discord.ui.Button(style=discord.ButtonStyle.green,label="Accept",emoji=self.bot.emoji.SUCCESS)
            accept_button.callback = lambda i: accept_economy_rules_callback(i)
            view.add_item(accept_button)
            async def accept_economy_rules_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.defer()
                    await interaction.response.defer()
                    user_data = cache.users.get(str(interaction.user.id),{})
                    if not user_data:
                        user_data = await databases.users.insert(user_id=interaction.user.id)
                    user_data = cache.users.get(str(interaction.user.id),{})
                    await databases.users.update(
                        id=user_data.get("id"),
                        economy_rules_accepted=True
                    )
                    await interaction.message.edit(content=f"{self.bot.emoji.SUCCESS} | {interaction.user.display_name} | Economy rules accepted",view=None,embed=None)
                except Exception as e:
                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
                    await interaction.message.edit(content=f"{self.bot.emoji.ERROR} | An error occured",view=None,embed=None)
            await ctx.reply(embed=embed,view=view,mention_author=True)
            return False
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
            return False


    @commands.command(
        name = "balance",
        help = "Check your balance",
        aliases = ["bal"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def balance(self, ctx:commands.Context):
        try:
            if not await self.accept_economy_rules(ctx):
                return
            user_data = cache.users.get(str(ctx.author.id),{})
            if not user_data:
                user_data = await databases.users.insert(user_id=ctx.author.id)
            user_data = cache.users.get(str(ctx.author.id),{})                
            await ctx.send(content=f"**- {ctx.author.display_name} | Your balance is: `{get_formatted_balance(user_data.get('balance',0))}` {self.bot.emoji.COIN}**")
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
            await ctx.send(f"An error occured: {e}")
        
    @commands.command(
        name="givebalance",
        help="Transfer balance to another user",
        aliases=["givebal","gbal"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def givebalance(self, ctx: commands.Context, user: discord.User, amount: int=1):
        try:
            if not await self.accept_economy_rules(ctx):
                return
            if amount <= 0:
                return await ctx.send(f"{self.bot.emoji.ERROR} Amount must be greater than 0",delete_after=10)
            if user.bot:
                return await ctx.send(f"{self.bot.emoji.ERROR} You can't give balance to a bot",delete_after=10)
            if ctx.author.id == user.id:
                return await ctx.send(f"{self.bot.emoji.ERROR} You can't give balance to yourself",delete_after=10)
            author_data = cache.users.get(str(ctx.author.id),{})
            user_data = cache.users.get(str(user.id),{})
            if not author_data:
                author_data = await databases.users.insert(user_id=ctx.author.id)
            if not user_data:
                user_data = await databases.users.insert(user_id=user.id)
            author_data = cache.users.get(str(ctx.author.id),{})
            user_data = cache.users.get(str(user.id),{})

            if (author_data.get("balance") if author_data.get("balance") else 0) < amount:
                return await ctx.send(f"{self.bot.emoji.ERROR} | {ctx.author.display_name} | You don't have enough balance to give",delete_after=10)

            max_dailt_transfer_limit = 50000
            if author_data.get("level",1) > 0:
                max_dailt_transfer_limit = max_dailt_transfer_limit*author_data.get("level",1)
            
            if (author_data.get("transfered_balance") if author_data.get("transfered_balance") else 0) + amount > max_dailt_transfer_limit:
                # make sure its the next date
                if (author_data.get("transfered_balance_at") if author_data.get("transfered_balance_at") else datetime.datetime.utcnow()).date() == datetime.datetime.utcnow().date():
                    return await ctx.send(f"{self.bot.emoji.ERROR} | {ctx.author.display_name} |  You Already Transfered `{get_formatted_balance(author_data.get('transfered_balance') if author_data.get('transfered_balance') else 0)}/{get_formatted_balance(max_dailt_transfer_limit)}` {self.bot.emoji.COIN} today",delete_after=30)
                else:
                    await databases.users.update(
                        id=author_data.get("id"),
                        transfered_balance=0,
                        transfered_balance_at=datetime.datetime.utcnow().isoformat()
                    )
                    author_data = cache.users.get(str(ctx.author.id),{})

            
            max_dailt_received_limit = 30000
            if user_data.get("level",1) > 0:
                max_dailt_received_limit = max_dailt_received_limit*user_data.get("level",1)


            if (user_data.get("received_balance") if user_data.get("received_balance") else 0)  + amount > max_dailt_received_limit:
                # make sure its the next date
                if (user_data.get("received_balance_at") if user_data.get("received_balance_at") else datetime.datetime.utcnow()).date() == datetime.datetime.utcnow().date():
                    return await ctx.send(f"{self.bot.emoji.ERROR} | {user.display_name} | Already Received `{get_formatted_balance(user_data.get('received_balance') if user_data.get('received_balance') else 0)}/{get_formatted_balance(max_dailt_received_limit)}` {self.bot.emoji.COIN} today",delete_after=30)
                else:
                    await databases.users.update(
                        id=user_data.get("id"),
                        received_balance=0,
                        received_balance_at=datetime.datetime.utcnow().isoformat()
                    )
                    user_data = cache.users.get(str(user.id),{})

            await databases.users.update(
                id=author_data.get("id"),
                balance=(author_data.get("balance") if author_data.get("balance") else 0) - amount,
                transfered_balance=(author_data.get("transfered_balance") if author_data.get("transfered_balance") else 0) + amount,
                transfered_balance_at=datetime.datetime.utcnow().isoformat()
            )
            await databases.users.update(
                id=user_data.get("id"),
                balance=(user_data.get("balance") if user_data.get("balance") else 0) + amount,
                received_balance=(user_data.get("received_balance") if user_data.get("received_balance") else 0) + amount,
                received_balance_at=datetime.datetime.utcnow().isoformat()
            )
            await ctx.send(f"**- {self.bot.emoji.TRANSFER} | {ctx.author.display_name} | Transferred `{get_formatted_balance(amount)}` {self.bot.emoji.COIN} to {user.display_name}**")

        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
            await ctx.send(f"An error occured: {e}")
    
    @commands.command(
        name="daily",
        help="Get your daily balance",
        aliases=["dailycash","dailyc"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def daily(self, ctx: commands.Context):
        try:
            if not await self.accept_economy_rules(ctx):
                return
            user_data = cache.users.get(str(ctx.author.id),{})
            if not user_data:
                user_data = await databases.users.insert(user_id=ctx.author.id)
            user_data = cache.users.get(str(ctx.author.id),{})

            if user_data.get("level",1) < 3:
                daily_coin = random.randint(500,700)
            elif 3 <= user_data.get("level",1) < 5:
                daily_coin = random.randint(700,900)
            elif 5 <= user_data.get("level",1) < 10:
                daily_coin = random.randint(900,1100)
            elif 10 <= user_data.get("level",1) < 15:
                daily_coin = random.randint(1100,2000)
            elif 15 <= user_data.get("level",1) < 20:
                daily_coin = random.randint(2000,5000)
            elif 20 <= user_data.get("level",1) < 25:
                daily_coin = random.randint(5000,10000)
            else:
                daily_coin = random.randint(100,5000)

            if user_data.get("daily_at"):
                if user_data.get("daily_at").date() == datetime.datetime.utcnow().date():
                    return await ctx.send(f"**- {self.bot.emoji.ERROR} | {ctx.author.display_name} | You already claimed your daily Gift today**")
            await databases.users.update(
                id=user_data.get("id"),
                balance=user_data.get("balance",0) + daily_coin,
                daily_at=datetime.datetime.utcnow().isoformat()
            )
            await ctx.send(f"**- {self.bot.emoji.DAILY} | {ctx.author.display_name} | You got `{get_formatted_balance(daily_coin)}` {self.bot.emoji.COIN} as daily Gift**")

        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
            await ctx.send(f"An error occured: {e}")

    @commands.command(
        name="memorymatch",
        help="Play a memory match game",
        aliases=["memory","mm"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=300, type=commands.BucketType.user)
    async def memorymatch(self, ctx: commands.Context):
        try:
            if not await self.accept_economy_rules(ctx):
                return
            user_data = cache.users.get(str(ctx.author.id), {})
            if not user_data:
                user_data = await databases.users.insert(user_id=ctx.author.id)
            user_data = cache.users.get(str(ctx.author.id), {})
            if user_data.get("balance", 0) < 500:
                return await ctx.send(f"**- {self.bot.emoji.ERROR} | {ctx.author.display_name} | You need at least `500` {self.bot.emoji.COIN} to play this game**")
            await databases.users.update(
                id=user_data.get("id"),
                balance=user_data.get("balance", 0) - 100
            )
            memory_match_emojis = self.bot.emoji.MEMORY_MATCH_EMOJIS
            emojis = random.choices(memory_match_emojis, k=10)
            shuffle_emojis = emojis.copy()
            random.shuffle(shuffle_emojis)


            cancled = False

            total_matches = 0

            total_clicks = 50

            query_clicked = []  # [row-col-emoji]


            async def get_embed():
                embed = discord.Embed(
                    title="Memory Match",
                    description=f"**Match the emojis to win\nEnds: <t:{int((start_time + datetime.timedelta(minutes=5)).timestamp())}:R>\n\nTotal Matches: `{total_matches}`\nTotal Clicks Left:` {total_clicks}`**",
                    color=color.blue
                )
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                embed.add_field(name="", value="", inline=False)
                embed.add_field(name="Emojis", value=" ".join(shuffle_emojis))
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
                embed.set_footer(text="You have 5 minutes to complete the game")
                return embed

            clicked_emojis = []  # [row-col-emoji]

            def count_matches():
                nonlocal clicked_emojis, total_matches
                matches = 0
                only_emojis = [x.split("-")[-1] for x in clicked_emojis]
                unique_emojis = set(only_emojis)  # Get unique emojis to avoid counting the same emoji multiple times

                for emoji in unique_emojis:
                    count = only_emojis.count(emoji)
                    matches += count // 2  # Each pair of the same emoji counts as one match

                total_matches = matches

            async def give_reward(user,min,max):
                reward = random.randint(min,max)
                user_data = cache.users.get(str(user.id),{})
                if not user_data:
                    user_data = await databases.users.insert(user_id=user.id)
                user_data = cache.users.get(str(user.id),{})
                await databases.users.update(
                    id=user_data.get("id"),
                    balance=user_data.get("balance",0) + reward
                )
                return reward


            async def memory_match_callback(interaction: discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="Not your game", color=color.red), ephemeral=True,delete_after=5)
                    nonlocal total_clicks, total_matches, clicked_emojis, query_clicked, cancled
                    custom_id = interaction.data.get('custom_id')

                    last_clicked_emoji = custom_id.split("-")[-1]

                    # update the view and set the emoji to the show temporarily
                    view = discord.ui.View.from_message(interaction.message)
                    for item in view.children:
                        if item.custom_id == custom_id:
                            item.disabled = True
                            item.emoji = last_clicked_emoji
                            break
                    await interaction.response.edit_message(view=view)

                    if custom_id in clicked_emojis:
                        return logger.info("Already clicked")

                    if len(query_clicked) > 0:
                        # Check if the current click matches the previous one
                        previous_custom_id = query_clicked[0]
                        previous_emoji = previous_custom_id.split("-")[-1]
                        current_emoji = custom_id.split("-")[-1]

                        if previous_emoji == current_emoji:
                            # It's a match
                            clicked_emojis.append(previous_custom_id)
                            clicked_emojis.append(custom_id)
                        else:
                            pass

                        # Clear the query_clicked list
                        query_clicked = []
                    else:
                        # Add the current click to the query_clicked list
                        query_clicked.append(custom_id)

                    count_matches()

                    total_clicks -= 1

                    if total_clicks == 0:
                        embed = discord.Embed(
                            title="Memory Match",
                            description=f"**{self.bot.emoji.ERROR} | Game ended due to no more clicks left\n\nTotal Matches: `{total_matches}`\nTotal Clicks Left:` {total_clicks}`**",
                            color=color.red
                        )
                        embed.set_footer(text="Game ended due to no more clicks left")
                        embed.add_field(name="Emojis", value=" ".join(shuffle_emojis))
                        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
                        embed.set_thumbnail(url=ctx.author.display_avatar.url)
                        await interaction.message.edit(embed=embed, view=None)
                        cancled = True
                        if total_matches >= 5:
                            min,max = 100,500
                        elif total_matches >= 7:
                            min,max = 500,900
                        elif total_matches >= 9:
                            min,max = 900,1000
                        else:
                            min,max = 100,200
                        reward = await give_reward(ctx.author,min,max)
                        await ctx.send(f"**- {self.bot.emoji.SUCCESS} | {ctx.author.display_name} | You got `{get_formatted_balance(reward)}` {self.bot.emoji.COIN} for playing the game**")
                        return

                    if total_matches == len(emojis):
                        embed = discord.Embed(
                            title="Memory Match",
                            description=f"**{self.bot.emoji.SUCCESS} | Game ended due to all matches found\n\nTotal Matches: `{total_matches}`\nTotal Clicks Left:` {total_clicks}`**",
                            color=color.green
                        )
                        embed.set_footer(text="Game ended due to all matches found")
                        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
                        embed.set_thumbnail(url=ctx.author.display_avatar.url)
                        await interaction.message.edit(embed=embed, view=await get_view())
                        cancled = True
                        # as much clicks left as the user has matches left he wil get more reward
                        if total_clicks >= 5:
                            min,max = 500,1000
                        elif total_clicks >= 7:
                            min,max = 1000,1500
                        elif total_clicks >= 9:
                            min,max = 1500,2000
                        elif total_clicks >= 20:
                            min,max = 2000,4000
                        else:
                            min,max = 100,500
                        reward = await give_reward(ctx.author,min,max)
                        await ctx.send(f"**- {self.bot.emoji.SUCCESS} | {ctx.author.display_name} | You got `{get_formatted_balance(reward)}` {self.bot.emoji.COIN} for playing the game**")
                        return

                    await interaction.message.edit(embed=await get_embed(), view=await get_view())

                except Exception as e:
                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            async def get_view():
                view = discord.ui.View(timeout=500)
                duplicate_emojis = emojis * 2  # Duplicate emojis to have enough for the grid

                # Make duplicate emojis 4 in a row
                rows = 5
                cols = 4
                grid_emojis = [duplicate_emojis[i:i + cols] for i in range(0, len(duplicate_emojis), cols)]

                for row_index, row in enumerate(grid_emojis):
                    for col_index, emoji in enumerate(row):
                        custom_id = f"{row_index}-{col_index}-{emoji}"
                        button = discord.ui.Button(
                            style=discord.ButtonStyle.primary,
                            emoji=emoji if (custom_id in clicked_emojis or custom_id in query_clicked) else self.bot.emoji.QUESTION,
                            row=row_index,
                            custom_id=custom_id,
                            disabled=custom_id in clicked_emojis or custom_id in query_clicked
                        )
                        # Correctly handle the callback to avoid closure issues
                        button.callback = lambda interaction, custom_id=custom_id: memory_match_callback(interaction)
                        view.add_item(button)
                return view

            start_time = datetime.datetime.now()
            message = await ctx.send(embed=await get_embed(), view=await get_view())
            await asyncio.sleep(300)
            if not cancled:
                embed = discord.Embed(
                    title="Memory Match",
                    description=f"**{self.bot.emoji.CREATED} | Game ended due to inactivity\nEnds: <t:{int((start_time + datetime.timedelta(minutes=5)).timestamp())}:R>\n\nTotal Matches: `{total_matches}`\nTotal Clicks Left:` {total_clicks}`**",
                    color=color.red
                )
                embed.set_footer(text="Game ended due to inactivity")
                embed.add_field(name="Emojis", value=" ".join(shuffle_emojis))
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                await message.edit(embed=embed, view=None)

        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")



    @commands.command(
        name="coinflip",
        help="Flip a coin",
        aliases=["cf"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def coinflip(self, ctx:commands.Context, amount:str="1", side:str="heads"):
        try:
            if side.lower() not in ["heads","tails"]:
                return await ctx.send(f"{self.bot.emoji.ERROR} | Side must be `heads` or `tails`",delete_after=10)
            max_bet = 100000
            try:
                if amount.lower() == "all":
                    amount = cache.users.get(str(ctx.author.id),{}).get("balance",0) if cache.users.get(str(ctx.author.id),{}).get("balance",0) < max_bet else max_bet
                else:
                    amount = int(amount)
            except:
                return await ctx.send(f"{self.bot.emoji.ERROR} | Amount must be a number",delete_after=10)                    
            if amount <= 0:
                return await ctx.send(f"{self.bot.emoji.ERROR} | Amount must be greater than 0",delete_after=10)
            if amount > max_bet:
                return await ctx.send(f"{self.bot.emoji.ERROR} | Amount must be less than {get_formatted_balance(max_bet)}",delete_after=10)
            user_data = cache.users.get(str(ctx.author.id),{})
            if not user_data:
                user_data = await databases.users.insert(user_id=ctx.author.id)
            user_data = cache.users.get(str(ctx.author.id),{})
            if user_data.get("balance",0) < amount:
                return await ctx.send(f"{self.bot.emoji.ERROR} | {ctx.author.display_name} | You don't have enough balance to bet",delete_after=10)
            message = await ctx.send(f"**- {self.bot.emoji.COIN_FLIPING} | {ctx.author.display_name} | Spending `{amount}` {self.bot.emoji.COIN} to `{side}`**")
            await databases.users.update(
                id=cache.users.get(str(ctx.author.id),{}).get("id"),
                balance=cache.users.get(str(ctx.author.id),{}).get("balance",0) - amount
            )
            await asyncio.sleep(random.randint(3,5))
            if side.lower() == random.choice(["heads","tails"]):
                reward = amount*2
                await databases.users.update(
                    id=cache.users.get(str(ctx.author.id),{}).get("id"),
                    balance=cache.users.get(str(ctx.author.id),{}).get("balance",0) + reward
                )
                return await message.edit(content=f"**- {self.bot.emoji.SUCCESS} | {ctx.author.display_name} | You won `{reward}` {self.bot.emoji.COIN}**")
            else:
                return await message.edit(content=f"**- {self.bot.emoji.FAILED} | {ctx.author.display_name} | You lost `{amount}` {self.bot.emoji.COIN}**")
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
    

    