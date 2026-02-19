import asyncio
import platform
import os
from typing import Optional, List
import io

import discord
from colorama import Fore, Style, init

init(autoreset=True)


class Logger:
    @staticmethod
    def success(message: str):
        print(f'{Fore.GREEN}✓{Style.RESET_ALL} {message}')

    @staticmethod
    def error(message: str):
        print(f'{Fore.RED}✗{Style.RESET_ALL} {message}')

    @staticmethod
    def warning(message: str):
        print(f'{Fore.YELLOW}⚠{Style.RESET_ALL} {message}')

    @staticmethod
    def info(message: str):
        print(f'{Fore.CYAN}➜{Style.RESET_ALL} {message}')

    @staticmethod
    def progress(message: str):
        print(f'{Fore.MAGENTA}⟳{Style.RESET_ALL} {message}')


class ServerCloner:
    def __init__(self, client):
        self.client = client
        self.logger = Logger()

    async def delete_roles_fast(self, guild: discord.Guild) -> None:
        self.logger.progress("Deleting roles...")
        roles_to_delete = [role for role in guild.roles if role.name != "@everyone"]
        
        if not roles_to_delete:
            return

        tasks = [self._delete_role(role) for role in roles_to_delete]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for result in results if result is True)
        self.logger.success(f"Deleted {success_count}/{len(roles_to_delete)} roles")

    async def _delete_role(self, role):
        try:
            await role.delete()
            return True
        except (discord.Forbidden, discord.HTTPException):
            return False

    async def create_roles_fast(self, copy_to_guild: discord.Guild, copy_from_guild: discord.Guild) -> None:
        self.logger.progress("Creating roles...")
        roles = [role for role in reversed(copy_from_guild.roles) if role.name != "@everyone"]
        
        if not roles:
            return

        created_count = 0
        for role in roles:
            try:
                await copy_to_guild.create_role(
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
        
        self.logger.success(f"Created {created_count}/{len(roles)} roles")

    async def delete_channels_fast(self, guild: discord.Guild) -> None:
        self.logger.progress("Deleting channels...")
        channels = list(guild.channels)
        
        if not channels:
            return
        
        tasks = [self._delete_channel(channel) for channel in channels]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(1 for result in results if result is True)
        self.logger.success(f"Deleted {success_count}/{len(channels)} channels")

    async def _delete_channel(self, channel):
        try:
            await channel.delete()
            return True
        except (discord.Forbidden, discord.HTTPException):
            return False

    async def create_categories_fast(self, copy_to_guild: discord.Guild, copy_from_guild: discord.Guild) -> None:
        self.logger.progress("Creating categories...")
        categories = list(copy_from_guild.categories)
        
        if not categories:
            return

        created_count = 0
        for category in categories:
            try:
                overwrites = {}
                for target, permissions in category.overwrites.items():
                    if isinstance(target, discord.Role):
                        if target.name == "@everyone":
                            overwrites[copy_to_guild.default_role] = permissions
                        else:
                            new_role = discord.utils.get(copy_to_guild.roles, name=target.name)
                            if new_role:
                                overwrites[new_role] = permissions
                    elif isinstance(target, discord.Member):
                        member = copy_to_guild.get_member(target.id)
                        if member:
                            overwrites[member] = permissions

                new_category = await copy_to_guild.create_category(
                    name=category.name,
                    overwrites=overwrites
                )
                await new_category.edit(position=category.position)
                created_count += 1
                await asyncio.sleep(0.1)
            except (discord.Forbidden, discord.HTTPException):
                pass
        
        self.logger.success(f"Created {created_count}/{len(categories)} categories")

    async def create_text_channels_fast(self, copy_to_guild: discord.Guild, copy_from_guild: discord.Guild) -> None:
        self.logger.progress("Creating text channels...")
        text_channels = list(copy_from_guild.text_channels)
        
        if not text_channels:
            return

        created_count = 0
        for channel in text_channels:
            try:
                category = None
                if channel.category:
                    category = discord.utils.get(copy_to_guild.categories, name=channel.category.name)

                overwrites = {}
                for target, permissions in channel.overwrites.items():
                    if isinstance(target, discord.Role):
                        if target.name == "@everyone":
                            overwrites[copy_to_guild.default_role] = permissions
                        else:
                            new_role = discord.utils.get(copy_to_guild.roles, name=target.name)
                            if new_role:
                                overwrites[new_role] = permissions
                    elif isinstance(target, discord.Member):
                        member = copy_to_guild.get_member(target.id)
                        if member:
                            overwrites[member] = permissions

                await copy_to_guild.create_text_channel(
                    name=channel.name,
                    overwrites=overwrites,
                    category=category,
                    position=channel.position,
                    topic=channel.topic,
                    slowmode_delay=channel.slowmode_delay,
                    nsfw=channel.nsfw
                )
                created_count += 1
                await asyncio.sleep(0.1)
            except Exception:
                pass
        
        self.logger.success(f"Created {created_count}/{len(text_channels)} text channels")

    async def create_voice_channels_fast(self, copy_to_guild: discord.Guild, copy_from_guild: discord.Guild) -> None:
        self.logger.progress("Creating voice channels...")
        voice_channels = list(copy_from_guild.voice_channels)
        
        if not voice_channels:
            return

        created_count = 0
        for channel in voice_channels:
            try:
                category = None
                if channel.category:
                    category = discord.utils.get(copy_to_guild.categories, name=channel.category.name)

                overwrites = {}
                for target, permissions in channel.overwrites.items():
                    if isinstance(target, discord.Role):
                        if target.name == "@everyone":
                            overwrites[copy_to_guild.default_role] = permissions
                        else:
                            new_role = discord.utils.get(copy_to_guild.roles, name=target.name)
                            if new_role:
                                overwrites[new_role] = permissions
                    elif isinstance(target, discord.Member):
                        member = copy_to_guild.get_member(target.id)
                        if member:
                            overwrites[member] = permissions

                await copy_to_guild.create_voice_channel(
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
        
        self.logger.success(f"Created {created_count}/{len(voice_channels)} voice channels")

    async def clone_emojis(self, copy_to_guild: discord.Guild, copy_from_guild: discord.Guild) -> None:
        self.logger.progress("Cloning emojis...")
        emojis = list(copy_from_guild.emojis)
        
        if not emojis:
            return

        cloned_count = 0
        
        for emoji in emojis:
            try:
                emoji_data = await emoji.read()
                await copy_to_guild.create_custom_emoji(
                    name=emoji.name,
                    image=emoji_data
                )
                cloned_count += 1
                await asyncio.sleep(0.25)
            except Exception:
                pass
        
        self.logger.success(f"Cloned {cloned_count}/{len(emojis)} emojis")

    async def clone_stickers(self, copy_to_guild: discord.Guild, copy_from_guild: discord.Guild) -> None:
        self.logger.progress("Cloning stickers (first 5)...")
        stickers = list(copy_from_guild.stickers)[:5] 
        
        if not stickers:
            self.logger.info("No stickers to clone")
            return

        cloned_count = 0
        
        for sticker in stickers:
            try:
                sticker_data = await sticker.read()
                sticker_bytes = io.BytesIO(sticker_data)
                
                await copy_to_guild.create_sticker(
                    name=sticker.name,
                    description=sticker.description or "Cloned sticker",
                    emoji=sticker.emoji,
                    file=discord.File(fp=sticker_bytes, filename=f"{sticker.name}.png")
                )
                cloned_count += 1
                await asyncio.sleep(0.3)
            except discord.HTTPException as e:
                if e.status == 429:
                    await asyncio.sleep(1)
            except Exception:
                pass
        
        total_stickers = len(copy_from_guild.stickers)
        if total_stickers > 5:
            self.logger.success(f"Cloned {cloned_count}/5 stickers (limited from {total_stickers} total)")
        else:
            self.logger.success(f"Cloned {cloned_count}/{total_stickers} stickers")

    async def update_guild_settings(self, copy_to_guild: discord.Guild, copy_from_guild: discord.Guild) -> None:
        self.logger.progress("Updating server settings...")
        
        try:
            await copy_to_guild.edit(name=copy_from_guild.name)
            self.logger.success(f"Updated name: {copy_from_guild.name}")
        except (discord.Forbidden, discord.HTTPException):
            self.logger.warning("Failed to update name")

        try:
            if copy_from_guild.icon:
                icon_data = await copy_from_guild.icon.read()
                await copy_to_guild.edit(icon=icon_data)
                self.logger.success("Updated icon")
        except (discord.Forbidden, discord.HTTPException):
            pass

        try:
            if copy_from_guild.banner:
                banner_data = await copy_from_guild.banner.read()
                await copy_to_guild.edit(banner=banner_data)
                self.logger.success("Updated banner")
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def clone_server(self, copy_from_guild_id: int, copy_to_guild_id: int) -> None:
        copy_from_guild = self.client.get_guild(copy_from_guild_id)
        copy_to_guild = self.client.get_guild(copy_to_guild_id)

        if not copy_from_guild:
            self.logger.error(f"Source server {copy_from_guild_id} not found")
            return
        if not copy_to_guild:
            self.logger.error(f"Target server {copy_to_guild_id} not found")
            return

        print(f"\n{Fore.CYAN}{'━'*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}┃ {Fore.WHITE}SOURCE:{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}{copy_from_guild.name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}┃ {Fore.WHITE}TARGET:{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}{copy_to_guild.name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'━'*60}{Style.RESET_ALL}\n")

        start_time = asyncio.get_event_loop().time()

        await self.update_guild_settings(copy_to_guild, copy_from_guild)
        await self.delete_roles_fast(copy_to_guild)
        await self.delete_channels_fast(copy_to_guild)
        await self.create_roles_fast(copy_to_guild, copy_from_guild)
        await self.create_categories_fast(copy_to_guild, copy_from_guild)
        await self.create_text_channels_fast(copy_to_guild, copy_from_guild)
        await self.create_voice_channels_fast(copy_to_guild, copy_from_guild)
        await self.clone_emojis(copy_to_guild, copy_from_guild)
        await self.clone_stickers(copy_to_guild, copy_from_guild)

        end_time = asyncio.get_event_loop().time()
        duration = round(end_time - start_time, 2)

        print(f"\n{Fore.GREEN}{'━'*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Clone completed successfully in {duration}s{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'━'*60}{Style.RESET_ALL}\n")


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    banner = f"""
{Fore.MAGENTA}╔════════════════════════════════════════════════════════════╗
║                                                            ║
║            {Fore.CYAN}▓█████▄  ██▓  ██████  ▄████▄   ▒█████   ██▀███  ▓█████▄{Fore.MAGENTA} ║
║            {Fore.CYAN}▒██▀ ██▌▓██▒▒██    ▒ ▒██▀ ▀█  ▒██▒  ██▒▓██ ▒ ██▒▒██▀ ██▌{Fore.MAGENTA}║
║            {Fore.CYAN}░██   █▌▒██▒░ ▓██▄   ▒▓█    ▄ ▒██░  ██▒▓██ ░▄█ ▒░██   █▌{Fore.MAGENTA}║
║            {Fore.CYAN}░▓█▄   ▌░██░  ▒   ██▒▒▓▓▄ ▄██▒▒██   ██░▒██▀▀█▄  ░▓█▄   ▌{Fore.MAGENTA}║
║            {Fore.CYAN}░▒████▓ ░██░▒██████▒▒▒ ▓███▀ ░░ ████▓▒░░██▓ ▒██▒░▒████▓{Fore.MAGENTA} ║
║            {Fore.CYAN} ▒▒▓  ▒ ░▓  ▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░░ ▒░▒░▒░ ░ ▒▓ ░▒▓░ ▒▒▓  ▒{Fore.MAGENTA} ║
║            {Fore.CYAN} ░ ▒  ▒  ▒ ░░ ░▒  ░ ░  ░  ▒     ░ ▒ ▒░   ░▒ ░ ▒░ ░ ▒  ▒{Fore.MAGENTA} ║
║            {Fore.CYAN} ░ ░  ░  ▒ ░░  ░  ░  ░        ░ ░ ░ ▒    ░░   ░  ░ ░  ░{Fore.MAGENTA} ║
║            {Fore.CYAN}   ░     ░        ░  ░ ░          ░ ░     ░        ░{Fore.MAGENTA}    ║
║            {Fore.CYAN} ░                  ░                            ░{Fore.MAGENTA}      ║
║                                                            ║
║              {Fore.WHITE}SERVER CLONER {Fore.LIGHTBLACK_EX}by poixt{Fore.MAGENTA}                       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def get_user_input():
    print(f"{Fore.CYAN}┌─ Configuration{Style.RESET_ALL}")
    token = input(f"{Fore.CYAN}├─ Token:{Style.RESET_ALL} ").strip()
    copy_from_guild_id = input(f"{Fore.CYAN}├─ Source Server ID (copy from):{Style.RESET_ALL} ").strip()
    copy_to_guild_id = input(f"{Fore.CYAN}└─ Target Server ID (paste to):{Style.RESET_ALL} ").strip()
    
    return token, copy_from_guild_id, copy_to_guild_id


async def main():
    clear_screen()
    print_banner()

    token, copy_from_guild_id, copy_to_guild_id = get_user_input()

    if not all([token, copy_from_guild_id, copy_to_guild_id]):
        print(f"\n{Fore.RED}✗ Missing required fields{Style.RESET_ALL}")
        input(f"\n{Fore.WHITE}Press Enter to exit...{Style.RESET_ALL}")
        return

    try:
        copy_from_guild_id = int(copy_from_guild_id)
        copy_to_guild_id = int(copy_to_guild_id)
    except ValueError:
        print(f"\n{Fore.RED}✗ Invalid server IDs{Style.RESET_ALL}")
        input(f"\n{Fore.WHITE}Press Enter to exit...{Style.RESET_ALL}")
        return

    client = discord.Client(self_bot=True)
    cloner = ServerCloner(client)

    @client.event
    async def on_ready():
        print(f"\n{Fore.GREEN}✓ Logged in as {Fore.WHITE}{client.user}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}➜ Accessible servers: {Fore.WHITE}{len(client.guilds)}{Style.RESET_ALL}\n")
        try:
            await asyncio.sleep(0.5)
            await cloner.clone_server(copy_from_guild_id, copy_to_guild_id)
        except Exception as e:
            print(f"\n{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")
        finally:
            await client.close()

    try:
        print(f"\n{Fore.CYAN}⟳ Connecting to Discord...{Style.RESET_ALL}")
        await client.login(token)
        await client.connect()
    except discord.LoginFailure:
        print(f"\n{Fore.RED}✗ Invalid token{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}✗ Connection error: {e}{Style.RESET_ALL}")
    
    input(f"\n{Fore.WHITE}Press Enter to exit...{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠ Operation cancelled by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}✗ Fatal error: {e}{Style.RESET_ALL}")
