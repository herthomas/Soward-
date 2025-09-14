import discord
from discord.ext import commands

from cogs.checks import checks

from themes import color
from functions import pings
import traceback,sys

import asyncio

from services.logging import logger

from core.Bot import AutoShardedBot

class Help(commands.Cog):
    cog_info = None
    def __init__(self, bot):
        self.bot:AutoShardedBot = bot
        class cog_info:
            name =  "Help"
            category = "Extra"
            description =  "Help commands"
            hidden =  False
            emoji = self.bot.emoji.HELP or "❓"
        # self.cog_info = cog_info
        self.all_app_commands = None

    @commands.hybrid_command(
        name="help",
        with_app_command=True,
        help="Show all commands in bot",
        aliases=["h"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=10,per=60,type=commands.BucketType.user)
    async def help(self,ctx:commands.Context):
        try:
            # show all commands in cogs and their description and other info by group of the cogs
            # and show the help command of the bot
            # get all cogs if the cog has cog_info in it then show the cog_info
            
            async def get_home_embed():
                embed = discord.Embed(
                    color=color.black,
                    description=""
                )
                extra_cogs = []
                main_cogs = []
                hidden_cogs = []

                all_commands_names = []
                for cog in self.bot.cogs:
                    cog = self.bot.get_cog(cog)
                    for command in cog.get_commands():
                        all_commands_names.append(command.name)
                
                for cog in self.bot.cogs:
                    cog = self.bot.get_cog(cog)
                    if hasattr(cog,"cog_info"):
                        if not cog.cog_info:
                            continue
                        if cog.cog_info.hidden:
                            hidden_cogs.append(cog)
                        elif cog.cog_info.category.lower() == "main":
                            main_cogs.append(cog)
                        elif cog.cog_info.category.lower() == "extra":
                            extra_cogs.append(cog)
                if main_cogs:
                    embed.add_field(
                        name="__Main__",
                        value="\n".join([f"> **{cog.cog_info.emoji} : {cog.cog_info.name}**" for cog in main_cogs]),
                        inline=True
                    )
                if extra_cogs:
                    embed.add_field(
                        name="__Extra__",
                        value="\n".join([f"> **{cog.cog_info.emoji} : {cog.cog_info.name}**" for cog in extra_cogs]),
                        inline=True
                    )
                # if hidden_cogs:
                #     if checks.check_is_admin_predicate(ctx.author):
                #         embed.add_field(
                #             name="__Hidden__",
                #             value="\n".join([f"> - **{cog.cog_info.emoji}  {cog.cog_info.name} ({len(cog.get_commands())})**" for cog in hidden_cogs]),
                #             inline=False
                #         )

                embed.description+=f"• Prefix for this server is ` {self.bot.cache.guilds.get(str(ctx.guild.id),{}).get('prefix',self.bot.BotConfig.PREFIX)} `"
                embed.description+=f"\n• Total commands:  ` {len(all_commands_names)} `"
                embed.description+=f"\n• [Get Soward]({self.bot.urls.INVITE}) | [Support server](https://discord.gg/soward) | [Vote me](https://top.gg/bot/1013771497157972008/vote)"
                # embed.description+=f"\n• Type `.help <command | module>` for more info."
                
                # embed.description+=f"\n• [Guidelines](https://discord.com/guidelines) | [Terms](https://discord.com/tos)"

                embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                embed.set_footer(
                    text=f"Made with ⚡ by Soward Development",
                    icon_url=self.bot.user.display_avatar.url
                )
                embed.set_author(
                    name=f"{self.bot.user.display_name}",
                    icon_url=self.bot.user.display_avatar.url,
                    url=self.bot.urls.WEBSITE
                )

                return embed

            timeout_time = 120
            cancled = False
            reported = False
            def reset_timeout(timeout:int=120):
                nonlocal timeout_time
                timeout_time = timeout

            async def get_home_view(disabled:bool=False):
                try:
                    view = discord.ui.View(timeout=120)
                    reset_timeout()

                    extra_cogs = []
                    main_cogs = []
                    hidden_cogs = []

                    all_commands_names = []
                    for cog in self.bot.cogs:
                        cog = self.bot.get_cog(cog)
                        for command in cog.get_commands():
                            all_commands_names.append(command.name)
                    

                    for cog in self.bot.cogs:
                        cog = self.bot.get_cog(cog)
                        if hasattr(cog,"cog_info"):
                            if not cog.cog_info:
                                continue
                            if cog.cog_info.hidden:
                                hidden_cogs.append(cog)
                            elif cog.cog_info.category.lower() == "main":
                                main_cogs.append(cog)
                            elif cog.cog_info.category.lower() == "extra":
                                extra_cogs.append(cog)
                    
                    all_commands_button = discord.ui.Button(
                        label="All Commands",
                        style=discord.ButtonStyle.green,
                        emoji=self.bot.emoji.COMMANDS,
                        row=1
                    )
                    all_commands_button.callback = lambda i: all_commands_button_callback(i)
                    view.add_item(all_commands_button)

                    report_button = discord.ui.Button(
                        label="Report",
                        style=discord.ButtonStyle.red,
                        emoji=self.bot.emoji.ERROR,
                        row=1
                    )
                    report_button.callback = lambda i: report_button_callback(i)
                    if reported:
                        report_button.disabled = True
                    view.add_item(report_button)

                    main_select_categorie = discord.ui.Select(
                        placeholder="Select a category to view",
                        options=[discord.SelectOption(
                            label=cog.cog_info.name,
                            value=cog.cog_info.name.lower(),
                            description=cog.cog_info.description,
                            emoji=cog.cog_info.emoji
                        ) for cog in main_cogs+extra_cogs],
                        row=0
                    )
                    main_select_categorie.callback = lambda i: select_categorie_callback(i)
                    view.add_item(main_select_categorie)


                    invite_me_button = discord.ui.Button(
                        label="Invite",
                        style=discord.ButtonStyle.link,
                        url=self.bot.urls.INVITE,
                        emoji=self.bot.emoji.INVITE,
                        row=2
                    )
                    view.add_item(invite_me_button)

                    support_server_button = discord.ui.Button(
                        label="Support",
                        style=discord.ButtonStyle.link,
                        url=self.bot.urls.SUPPORT_SERVER,
                        emoji=self.bot.emoji.SUPPORT,
                        row=2
                    )
                    view.add_item(support_server_button)



                    if disabled:
                        for item in view.children:
                            item.disabled = True
                    return view
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                    return None
                
            async def report_button_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this button",
                                color=color.red
                            ),
                            ephemeral=True,
                            delete_after=10
                        )
                    
                    class report_submit_modal(discord.ui.Modal,title="Submit Report"):
                        report_title_field = discord.ui.TextInput(
                            placeholder="Report Title",
                            label="Report Title",
                            required=True,
                            row=0,
                            style=discord.TextStyle.short
                        )
                        report_description_field = discord.ui.TextInput(
                            placeholder="Report Description",
                            label="Report Description",
                            required=True,
                            row=1,
                            style=discord.TextStyle.long
                        )
                        report_attachment_field = discord.ui.TextInput(
                            placeholder="Saparate the links with comma",
                            label="Report Attachment links",
                            required=False,
                            row=2,
                            style=discord.TextStyle.long
                        )
                        bot = self.bot
                        async def on_submit(self,interaction:discord.Interaction):
                            try:
                                title = self.report_title_field.value
                                description = self.report_description_field.value
                                attachments = self.report_attachment_field.value.split(",")
                                if not title or not description:
                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="Title and Description are required",
                                            color=color.red
                                        ),
                                        ephemeral=True,
                                        delete_after=10
                                    )
                                embed = discord.Embed(
                                    title=title,
                                    description=description,
                                    color=color.black
                                )
                                if attachments:
                                    embed.add_field(
                                        name="Attachments links",
                                        value="\n".join(attachments),
                                        inline=False
                                    )
                                embed.set_footer(
                                    text=f"Reported by {interaction.user.display_name} | {interaction.user.id}",
                                    icon_url=interaction.user.display_avatar.url
                                )
                                embed.set_author(
                                    name=f"{ctx.author.display_name}",
                                    icon_url=ctx.author.display_avatar.url
                                )
                                await interaction.response.defer(thinking=True,ephemeral=True)
                                channel = self.bot.get_channel(self.bot.channels.report_channel)
                                if not channel:
                                    return logger.error(f"Report channel not found. Channel ID: {self.bot.channels.report_channel}")
                                await channel.send(embed=embed)
                                nonlocal reported
                                reported = True
                                await interaction.edit_original_response(embed=discord.Embed(
                                    description="Report submitted successfully",
                                    color=color.green
                                ))
                            except Exception as e:
                                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                    
                    await interaction.response.send_modal(report_submit_modal())



                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")


            async def all_commands_button_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this button",
                                color=color.red
                            ),
                            ephemeral=True,
                            delete_after=10
                        )
                    extra_cogs = []
                    main_cogs = []
                    hidden_cogs = []

                    all_commands_names = []
                    for cog in self.bot.cogs:
                        cog = self.bot.get_cog(cog)
                        for command in cog.get_commands():
                            all_commands_names.append(command.name)
                    for cog in self.bot.cogs:
                        cog = self.bot.get_cog(cog)
                        if hasattr(cog,"cog_info"):
                            if not cog.cog_info:
                                continue
                            if cog.cog_info.hidden:
                                hidden_cogs.append(cog)
                            elif cog.cog_info.category.lower() == "main":
                                main_cogs.append(cog)
                            elif cog.cog_info.category.lower() == "extra":
                                extra_cogs.append(cog)
                    
                    embed = discord.Embed(
                        color=color.black
                    )
                    for cog in main_cogs+extra_cogs:
                        embed.add_field(
                            name=f"**{cog.cog_info.emoji} {cog.cog_info.name} [{len(cog.get_commands())}]**",
                            value=" | ".join([f"**`{command.name}`**" for command in cog.get_commands()]),
                            inline=False
                        )
                    embed.set_footer(
                        text=f"Made with ⚡ by Soward Development",
                        icon_url=self.bot.user.display_avatar.url
                    )
                    embed.set_author(
                        name=f"{self.bot.user.display_name}",
                        icon_url=self.bot.user.display_avatar.url,
                        url=self.bot.urls.WEBSITE
                    )
                    embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                    await interaction.response.edit_message(embed=embed,view=await get_home_view(disabled=True))
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            

            async def select_categorie_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this select menu",
                                color=color.red
                            ),
                            ephemeral=True,
                            delete_after=10
                        )
                    
                    value = interaction.data["values"][0]
                    
                    def get_selected_cog(name):
                        for cog in self.bot.cogs:
                            if cog.lower() == name:
                                return self.bot.get_cog(cog)
                        return None
                        
                    cog = get_selected_cog(value)

                    async def get_selected_cog_embed(cog):
                        try:
                            embed = discord.Embed(
                                title=f"{cog.cog_info.name} Commands",
                                description=f"{cog.cog_info.description}",
                                color=color.black
                            )
                            all_commands = cog.get_commands()

                            # all_commands to 5 list in list
                            all_commands = [all_commands[i:i+5] for i in range(0,len(all_commands),5)]

                            for lines in all_commands:
                                embed.description += f"\n>  - {' | '.join([f'**`{command.name}`**' for command in lines])}"

                            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                            embed.set_footer(
                                text=f"Made with ⚡ by Soward Development",
                                icon_url=self.bot.user.display_avatar.url
                            )
                            embed.set_author(
                                name=f"{self.bot.user.display_name}",
                                icon_url=self.bot.user.display_avatar.url,
                                url=self.bot.urls.WEBSITE
                            )
                            return embed                        
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                            return None
                    
                    async def get_selected_cog_view(disabled:bool=False):
                        try:
                            view = discord.ui.View(timeout=120)
                            reset_timeout()

                            all_commands = cog.get_commands()

                            command_select = discord.ui.Select(
                                placeholder="Select a command to view",
                                options=[discord.SelectOption(
                                    label=command.name,
                                    value=command.name,
                                    description=command.help
                                ) for command in all_commands],
                                row=0
                            )
                            command_select.callback = lambda i: command_select_callback(i)

                            view.add_item(command_select)

                            back_button = discord.ui.Button(
                                label="Back",
                                style=discord.ButtonStyle.secondary,
                                row=1,
                                emoji=self.bot.emoji.BACK
                            )
                            back_button.callback = lambda i: back_button_callback(i)
                            view.add_item(back_button)

                            if disabled:
                                for item in view.children:
                                    item.disabled = True
                    
                            return view
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                            return None
                        
                    async def command_select_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != ctx.author.id:
                                return await interaction.response.send_message(
                                    embed=discord.Embed(
                                        description="You are not allowed to use this select menu",
                                        color=color.red
                                    ),
                                    ephemeral=True,
                                    delete_after=10
                                )
                            
                            value = interaction.data["values"][0]
                            command = None
                            for cmd in cog.get_commands():
                                if cmd.name == value:
                                    command = cmd
                                    break
                            if not command:
                                return await interaction.response.send_message(
                                    embed=discord.Embed(
                                        description="Command not found",
                                        color=color.red
                                    ),
                                    ephemeral=True,
                                    delete_after=10
                                )

                            async def get_selected_command_embed():
                                try:
                                    embed = discord.Embed(
                                        title=f"{command.name} Command",
                                        description=f"{command.help}" if command.help else "",
                                        color=color.black
                                    )
                                    # if command has subcommands
                                    if not self.all_app_commands:
                                        self.all_app_commands = await self.bot.tree.fetch_commands()
                                    
                                    def get_app_command(name):
                                        for cmd in self.all_app_commands:
                                            if cmd.name == name:
                                                return cmd
                                        return None
                                    
                                    app_command = get_app_command(command.name)
                                    
                                    if app_command:
                                        if app_command.options:
                                            embed.description += f"\n\n**• Primary Command:** `{self.bot.BotConfig.PREFIX}{app_command.name} {' '.join([f'<{arg}>' for arg in command.clean_params])}`"
                                            embed.description += f"\n\n**• Options:**\n"
                                            for option in app_command.options:
                                                embed.description += f"\n> {option.mention if hasattr(option,"mention") else f'{self.bot.BotConfig.PREFIX}{command.name} {option.name}'}\n> {option.description}\n"
                                        else:
                                            embed.description += f"\n\n**• Primary Command:** {app_command.mention if hasattr(app_command,"mention") else f'{self.bot.BotConfig.PREFIX}{command.name}'}"
                                    else:
                                        embed.description += f"\n\n**• Primary Command:** `{self.bot.BotConfig.PREFIX}{command.name} {' '.join([f'<{arg}>' for arg in command.clean_params])}`"
                                        if hasattr(command,"commands"):
                                            embed.description += f"\n\n**• Subcommands:**\n"
                                            for subcommand in command.commands:
                                                embed.description += f"\n> **`{self.bot.BotConfig.PREFIX}{command.name} {subcommand.name} {' '.join([f'<{arg}>' for arg in subcommand.clean_params])}`** \n> {subcommand.help}\n"

                                    embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                                    embed.set_footer(
                                        text=f"Made with ⚡ by Soward Development",
                                        icon_url=self.bot.user.display_avatar.url
                                    )
                                    embed.set_author(
                                        name=f"{self.bot.user.display_name}",
                                        icon_url=self.bot.user.display_avatar.url,
                                        url=self.bot.urls.WEBSITE
                                    )
                                    return embed
                                except Exception as e:
                                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                                    return None
                            
                            async def get_selected_command_view(disabled:bool=False):
                                try:
                                    view = discord.ui.View(timeout=120)
                                    reset_timeout()

                                    back_button = discord.ui.Button(
                                        label="Back",
                                        style=discord.ButtonStyle.secondary,
                                        row=1,
                                        emoji=self.bot.emoji.BACK
                                    )
                                    back_button.callback = lambda i: back_button_callback(i)
                                    view.add_item(back_button)

                                    if disabled:
                                        for item in view.children:
                                            item.disabled = True
                                    return view
                                except Exception as e:
                                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                                    return None


                            async def back_button_callback(interaction:discord.Interaction):
                                try:
                                    if interaction.user.id != ctx.author.id:
                                        return await interaction.response.send_message(
                                            embed=discord.Embed(
                                                description="You are not allowed to use this select menu",
                                                color=color.red
                                            ),
                                            ephemeral=True,
                                            delete_after=10
                                        )
                                    await interaction.response.edit_message(embed=await get_selected_cog_embed(cog),view=await get_selected_cog_view(disabled=False))
                                except Exception as e:
                                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}")



                            await interaction.response.edit_message(embed=await get_selected_command_embed(),view=await get_selected_command_view())
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                    
                    async def back_button_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != ctx.author.id:
                                return await interaction.response.send_message(
                                    embed=discord.Embed(
                                        description="You are not allowed to use this select menu",
                                        color=color.red
                                    ),
                                    ephemeral=True,
                                    delete_after=10
                                )
                            await interaction.response.edit_message(embed=await get_home_embed(),view=await get_home_view())
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}")
                    await interaction.response.edit_message(embed=await get_selected_cog_embed(cog),view=await get_selected_cog_view(disabled=False))
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")



            message = await ctx.send(embed=await get_home_embed(),view=await get_home_view())

            while not cancled:
                timeout_time -= 1
                if timeout_time <= 0:
                    try:
                        await message.edit(embed=await get_home_embed(),view=await get_home_view(disabled=True))
                    except:
                        pass
                    break
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")