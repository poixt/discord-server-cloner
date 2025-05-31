import asyncio
import platform
import os
from typing import Optional

import discord
from colorama import Fore, Style, init

init(autoreset=True)


class Logger:
    @staticmethod
    def success(message: str):
        print(f'{Fore.LIGHTGREEN_EX}[+]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}{message}{Style.RESET_ALL}')

    @staticmethod
    def error(message: str):
        print(f'{Fore.LIGHTRED_EX}[!]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}{message}{Style.RESET_ALL}')

    @staticmethod
    def warning(message: str):
        print(f'{Fore.LIGHTYELLOW_EX}[~]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}{message}{Style.RESET_ALL}')

    @staticmethod
    def info(message: str):
        print(f'{Fore.LIGHTCYAN_EX}[*]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}{message}{Style.RESET_ALL}')

    @staticmethod
    def progress(message: str):
        print(f'{Fore.LIGHTMAGENTA_EX}[>]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}{message}{Style.RESET_ALL}')

    @staticmethod
    def step(message: str):
        print(f'{Fore.LIGHTBLUE_EX}[>>]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}{message}{Style.RESET_ALL}')


class ServerCloner:
    def __init__(self, client):
        self.client = client
        self.logger = Logger()

    async def delete_roles_fast(self, guild: discord.Guild) -> None:
        self.logger.step("Cleaning existing roles...")
        roles_to_delete = [role for role in guild.roles if role.name != "@everyone"]
        
        if not roles_to_delete:
            self.logger.info("No roles to clean")
            return

        tasks = []
        for role in roles_to_delete:
            tasks.append(self._delete_role(role))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for result in results if result is True)
        self.logger.success(f"Cleaned {Fore.LIGHTCYAN_EX}{success_count}{Style.RESET_ALL}/{Fore.LIGHTCYAN_EX}{len(roles_to_delete)}{Style.RESET_ALL} roles")

    async def _delete_role(self, role):
        try:
            await role.delete()
            return True
        except (discord.Forbidden, discord.HTTPException):
            return False

    async def create_roles_fast(self, target_guild: discord.Guild, source_guild: discord.Guild) -> None:
        self.logger.step("Creating server roles...")
        roles = [role for role in reversed(source_guild.roles) if role.name != "@everyone"]
        
        if not roles:
            self.logger.info("No roles to create")
            return

        created_count = 0
        for role in roles:
            try:
                await target_guild.create_role(
                    name=role.name,
                    permissions=role.permissions,
                    colour=role.colour,
                    hoist=role.hoist,
                    mentionable=role.mentionable
                )
                created_count += 1
                await asyncio.sleep(0.1)
            except (discord.Forbidden, discord.HTTPException):
                pass
        
        self.logger.success(f"Created {Fore.LIGHTBLUE_EX}{created_count}{Style.RESET_ALL}/{Fore.LIGHTBLUE_EX}{len(roles)}{Style.RESET_ALL} roles")

    async def delete_channels_fast(self, guild: discord.Guild) -> None:
        self.logger.step("Clearing existing channels...")
        channels = list(guild.channels)
        
        if not channels:
            self.logger.info("No channels to clear")
            return
        
        tasks = []
        for channel in channels:
            tasks.append(self._delete_channel(channel))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(1 for result in results if result is True)
        self.logger.success(f"Cleared {Fore.LIGHTYELLOW_EX}{success_count}{Style.RESET_ALL}/{Fore.LIGHTYELLOW_EX}{len(channels)}{Style.RESET_ALL} channels")

    async def _delete_channel(self, channel):
        try:
            await channel.delete()
            return True
        except (discord.Forbidden, discord.HTTPException):
            return False

    async def create_categories_fast(self, target_guild: discord.Guild, source_guild: discord.Guild) -> None:
        self.logger.step("Building category structure...")
        categories = list(source_guild.categories)
        
        if not categories:
            self.logger.info("No categories to create")
            return

        created_count = 0
        for category in categories:
            try:
                overwrites = {}
                for target, permissions in category.overwrites.items():
                    if isinstance(target, discord.Role):
                        new_role = discord.utils.get(target_guild.roles, name=target.name)
                        if new_role:
                            overwrites[new_role] = permissions

                new_category = await target_guild.create_category(
                    name=category.name,
                    overwrites=overwrites
                )
                await new_category.edit(position=category.position)
                created_count += 1
                await asyncio.sleep(0.2)
            except (discord.Forbidden, discord.HTTPException):
                pass
        
        self.logger.success(f"Built {Fore.LIGHTMAGENTA_EX}{created_count}{Style.RESET_ALL}/{Fore.LIGHTMAGENTA_EX}{len(categories)}{Style.RESET_ALL} categories")

    async def create_text_channels_fast(self, target_guild: discord.Guild, source_guild: discord.Guild) -> None:
        self.logger.step("Creating text channels...")
        text_channels = list(source_guild.text_channels)
        
        if not text_channels:
            self.logger.info("No text channels to create")
            return

        created_count = 0
        for channel in text_channels:
            try:
                category = None
                if channel.category:
                    category = discord.utils.get(target_guild.categories, name=channel.category.name)

                overwrites = {}
                for target, permissions in channel.overwrites.items():
                    if isinstance(target, discord.Role):
                        new_role = discord.utils.get(target_guild.roles, name=target.name)
                        if new_role:
                            overwrites[new_role] = permissions

                await target_guild.create_text_channel(
                    name=channel.name,
                    overwrites=overwrites,
                    category=category,
                    position=channel.position,
                    topic=channel.topic,
                    slowmode_delay=channel.slowmode_delay,
                    nsfw=channel.nsfw
                )
                created_count += 1
                await asyncio.sleep(0.15)
            except Exception:
                pass
        
        self.logger.success(f"Created {Fore.LIGHTYELLOW_EX}{created_count}{Style.RESET_ALL}/{Fore.LIGHTYELLOW_EX}{len(text_channels)}{Style.RESET_ALL} text channels")

    async def create_voice_channels_fast(self, target_guild: discord.Guild, source_guild: discord.Guild) -> None:
        self.logger.step("Creating voice channels...")
        voice_channels = list(source_guild.voice_channels)
        
        if not voice_channels:
            self.logger.info("No voice channels to create")
            return

        created_count = 0
        for channel in voice_channels:
            try:
                category = None
                if channel.category:
                    category = discord.utils.get(target_guild.categories, name=channel.category.name)

                overwrites = {}
                for target, permissions in channel.overwrites.items():
                    if isinstance(target, discord.Role):
                        new_role = discord.utils.get(target_guild.roles, name=target.name)
                        if new_role:
                            overwrites[new_role] = permissions

                await target_guild.create_voice_channel(
                    name=channel.name,
                    overwrites=overwrites,
                    category=category,
                    position=channel.position,
                    bitrate=channel.bitrate,
                    user_limit=channel.user_limit
                )
                created_count += 1
                await asyncio.sleep(0.15)
            except Exception:
                pass
        
        self.logger.success(f"Created {Fore.LIGHTCYAN_EX}{created_count}{Style.RESET_ALL}/{Fore.LIGHTCYAN_EX}{len(voice_channels)}{Style.RESET_ALL} voice channels")

    async def update_guild_settings(self, target_guild: discord.Guild, source_guild: discord.Guild) -> None:
        self.logger.step("Updating server settings...")
        
        settings_updated = 0
        
        try:
            await target_guild.edit(name=source_guild.name)
            settings_updated += 1
            self.logger.success(f"Server name: {Fore.LIGHTGREEN_EX}{source_guild.name}{Style.RESET_ALL}")
        except (discord.Forbidden, discord.HTTPException):
            self.logger.warning("Could not update server name")

        try:
            if source_guild.icon:
                icon_data = await source_guild.icon.read()
                await target_guild.edit(icon=icon_data)
                settings_updated += 1
                self.logger.success("Server icon updated")
        except (discord.Forbidden, discord.HTTPException):
            self.logger.warning("Could not update server icon")

        await self.handle_community_features(target_guild, source_guild)

    async def handle_community_features(self, target_guild: discord.Guild, source_guild: discord.Guild) -> None:
        self.logger.step("Configuring community features...")
        
        if hasattr(source_guild, 'community') and source_guild.community:
            try:
                if not target_guild.community:
                    rules_channel = None
                    updates_channel = None
                    
                    for channel in target_guild.text_channels:
                        if 'rule' in channel.name.lower():
                            rules_channel = channel
                        if 'announcement' in channel.name.lower() or 'update' in channel.name.lower():
                            updates_channel = channel
                    
                    if not rules_channel:
                        rules_channel = await target_guild.create_text_channel('rules')
                    if not updates_channel:
                        updates_channel = await target_guild.create_text_channel('announcements')
                    
                    await target_guild.edit(
                        community=True,
                        rules_channel=rules_channel,
                        public_updates_channel=updates_channel
                    )
                    self.logger.success("Community features enabled")
                else:
                    self.logger.info("Community already enabled")
            except (discord.Forbidden, discord.HTTPException) as e:
                self.logger.warning(f"Could not enable community features: {type(e).__name__}")
        else:
            self.logger.info("Source server doesn't have community features")

    async def clone_server(self, source_guild_id: int, target_guild_id: int) -> None:
        source_guild = self.client.get_guild(source_guild_id)
        target_guild = self.client.get_guild(target_guild_id)

        if not source_guild:
            self.logger.error(f"Source server {Fore.LIGHTRED_EX}{source_guild_id}{Style.RESET_ALL} not found or not accessible")
            return
        if not target_guild:
            self.logger.error(f"Target server {Fore.LIGHTRED_EX}{target_guild_id}{Style.RESET_ALL} not found or not accessible")
            return

        print(f"\n{Fore.LIGHTMAGENTA_EX}{'═' * 80}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}║{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}INITIATING SERVER CLONING OPERATION{Style.RESET_ALL} {Fore.LIGHTMAGENTA_EX}{'║':>28}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}╠{'═' * 78}╣{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}║{Style.RESET_ALL} {Fore.LIGHTCYAN_EX}SOURCE:{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}{source_guild.name[:50]}{Style.RESET_ALL} {Fore.LIGHTMAGENTA_EX}{'║':>{68-len(source_guild.name[:50])}}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}║{Style.RESET_ALL} {Fore.LIGHTBLUE_EX}TARGET:{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}{target_guild.name[:50]}{Style.RESET_ALL} {Fore.LIGHTMAGENTA_EX}{'║':>{68-len(target_guild.name[:50])}}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}║{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}f{Style.RESET_ALL} {Fore.LIGHTMAGENTA_EX}{'║':>18}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}{'═' * 80}{Style.RESET_ALL}\n")

        start_time = asyncio.get_event_loop().time()

        await self.update_guild_settings(target_guild, source_guild)
        await self.delete_roles_fast(target_guild)
        await self.delete_channels_fast(target_guild)
        await self.create_roles_fast(target_guild, source_guild)
        await self.create_categories_fast(target_guild, source_guild)
        await self.create_text_channels_fast(target_guild, source_guild)
        await self.create_voice_channels_fast(target_guild, source_guild)

        end_time = asyncio.get_event_loop().time()
        duration = round(end_time - start_time, 2)

        print(f"\n{Fore.LIGHTGREEN_EX}{'═' * 70}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}║{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}CLONING OPERATION COMPLETED SUCCESSFULLY{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}{'║':>15}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}╠{'═' * 68}╣{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}║{Style.RESET_ALL} {Fore.LIGHTCYAN_EX}DURATION:{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}{duration}s{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}{'║':>{55-len(str(duration))}}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}║{Style.RESET_ALL} {Fore.LIGHTMAGENTA_EX}STATUS:{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}OPERATION COMPLETE{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}{'║':>40}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}{'═' * 70}{Style.RESET_ALL}")


def clear_screen():
    system_name = platform.system().lower()
    if system_name == "windows":
        os.system("cls")
    elif system_name in ["linux", "darwin"]:
        os.system("clear")
    else:
        print("\n" * 50)


def print_banner():
    
    gradient_line1 = f"{chr(27)}[38;5;54m"  # Dark purple
    gradient_line2 = f"{chr(27)}[38;5;55m"  # Purple
    gradient_line3 = f"{chr(27)}[38;5;56m"  # Medium purple
    gradient_line4 = f"{chr(27)}[38;5;93m"  # Light purple
    gradient_line5 = f"{chr(27)}[38;5;129m" # Purple-magenta
    gradient_line6 = f"{chr(27)}[38;5;165m" # Magenta
    gradient_line7 = f"{chr(27)}[38;5;201m" # Bright magenta
    
    banner = f"""
{gradient_line1}    .________._______ ._______._______ _____._.______  ._______     ._______ .___    ._______  .______  ._______.______  {Style.RESET_ALL}
{gradient_line2}    |    ___/: ____  |: .____/:_.  ___\\__ _:|: __   \\ : .____/     :_.  ___\\|   |   : .___  \\ :      \\ : .____/: __   \\ {Style.RESET_ALL}
{gradient_line3}    |___    \\|    :  || : _/\\ |  : |/\\   |  :||  \\____|| : _/\\      |  : |/\\ |   |   | :   |  ||       || : _/\\ |  \\____|{Style.RESET_ALL}
{gradient_line4}    |       /|   |___||   /  \\|    /  \\  |   ||   :  \\ |   /  \\     |    /  \\|   |/\\ |     :  ||   |   ||   /  \\|   :  \\ {Style.RESET_ALL}
{gradient_line5}    |__:___/ |___|    |_.: __/|. _____/  |   ||   |___\\|_.: __/     |. _____/|   /  \\ \\_. ___/ |___|   ||_.: __/|   |___\\{Style.RESET_ALL}
{gradient_line6}       :                 :/    :/        |___||___|       :/         :/      |______/   :/         |___|   :/   |___|    {Style.RESET_ALL}
{gradient_line7}                               :                                     :                  :                                 {Style.RESET_ALL}


{Fore.MAGENTA}                                     Made by poixt{Style.RESET_ALL}
    """
    print(banner)


def get_user_input():
    print(f"\n{Fore.LIGHTCYAN_EX}╔═══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}║{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}CONFIGURATION SETUP{Style.RESET_ALL} {Fore.LIGHTCYAN_EX}{'║':>46}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    token = input(f"\n{Fore.LIGHTMAGENTA_EX}[>]{Style.RESET_ALL} {Fore.LIGHTCYAN_EX}Discord Token:{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}").strip()
    source_guild_id = input(f"{Fore.LIGHTMAGENTA_EX}[>]{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}Source Server ID:{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}").strip()
    target_guild_id = input(f"{Fore.LIGHTMAGENTA_EX}[>]{Style.RESET_ALL} {Fore.LIGHTBLUE_EX}Target Server ID:{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}").strip()
    
    print(f"{Style.RESET_ALL}")
    return token, source_guild_id, target_guild_id


async def main():
    clear_screen()
    print_banner()

    token, source_guild_id, target_guild_id = get_user_input()

    if not all([token, source_guild_id, target_guild_id]):
        print(f"\n{Fore.LIGHTRED_EX}[!]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}All configuration fields are required to proceed{Style.RESET_ALL}")
        input(f"\n{Fore.LIGHTYELLOW_EX}[>]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Press Enter to exit...{Style.RESET_ALL}")
        return

    try:
        source_guild_id = int(source_guild_id)
        target_guild_id = int(target_guild_id)
    except ValueError:
        print(f"\n{Fore.LIGHTRED_EX}[!]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Server IDs must be valid numeric values{Style.RESET_ALL}")
        input(f"\n{Fore.LIGHTYELLOW_EX}[>]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Press Enter to exit...{Style.RESET_ALL}")
        return

    client = discord.Client(self_bot=True)
    cloner = ServerCloner(client)

    @client.event
    async def on_ready():
        print(f"\n{Fore.LIGHTGREEN_EX}[+]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Successfully authenticated as:{Style.RESET_ALL} {Fore.LIGHTBLUE_EX}{client.user}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}[*]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Connected to {Fore.LIGHTMAGENTA_EX}{len(client.guilds)}{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}servers{Style.RESET_ALL}")
        try:
            await asyncio.sleep(0.5)
            await cloner.clone_server(source_guild_id, target_guild_id)
        except Exception as e:
            print(f"\n{Fore.LIGHTRED_EX}[!]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Critical error during cloning: {Fore.LIGHTRED_EX}{e}{Style.RESET_ALL}")
        finally:
            print(f"\n{Fore.LIGHTYELLOW_EX}[>]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Closing connection...{Style.RESET_ALL}")
            await client.close()

    try:
        print(f"\n{Fore.LIGHTCYAN_EX}[>]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Establishing connection...{Style.RESET_ALL}")
        await client.login(token)
        await client.connect()
    except discord.LoginFailure:
        print(f"\n{Fore.LIGHTRED_EX}[!]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Authentication failed - please verify your token{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.LIGHTRED_EX}[!]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Connection error: {Fore.LIGHTRED_EX}{e}{Style.RESET_ALL}")
    
    input(f"\n{Fore.LIGHTYELLOW_EX}[>]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Press Enter to exit...{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.LIGHTYELLOW_EX}[~]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Operation cancelled by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.LIGHTRED_EX}[!]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Unexpected error: {Fore.LIGHTRED_EX}{e}{Style.RESET_ALL}")
        input(f"\n{Fore.LIGHTYELLOW_EX}[>]{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Press Enter to exit...{Style.RESET_ALL}")