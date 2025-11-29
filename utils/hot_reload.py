import os
import pathlib

import discord
from discord.ext import commands, tasks
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv('.env'))

def path_from_extension(extension: str) -> pathlib.Path:
    return pathlib.Path(extension.replace(".", os.sep) + ".py")


class HotReload(commands.Cog):
    """
    Cog for reloading extensions as soon as the file is edited.
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.hot_reload_loop.start()

    def cog_unload(self):
        self.hot_reload_loop.stop()

    @tasks.loop(seconds=3)
    async def hot_reload_loop(self):
        for extension in list(self.bot.extensions.keys()):
            if extension in ["jishaku"]:
                continue
            path = path_from_extension(extension)
            time = os.path.getmtime(path)

            try:
                if self.last_modified_time[extension] == time:
                    continue
            except KeyError:
                self.last_modified_time[extension] = time

            try:
                await self.bot.reload_extension(extension)
            except commands.ExtensionNotLoaded:
                continue
            except commands.ExtensionError:
                pass
            else:
                # Send a log
                print(config("CUSTOM_GUILD_ID"))
                guild = self.bot.get_guild(int(config("CUSTOM_GUILD_ID")))
                print(guild)
                channel = guild.get_channel(int(config("JISHAKU_LOGGING_CHANNEL")))
                await channel.send(f"Reloaded extension: {extension}")
            finally:
                self.last_modified_time[extension] = time

    @hot_reload_loop.before_loop
    async def cache_last_modified_time(self):
        self.last_modified_time = {}
        for extension in self.bot.extensions.keys():
            if extension in ["jishaku"]:
                continue
            path = path_from_extension(extension)
            time = os.path.getmtime(path)
            self.last_modified_time[extension] = time


async def setup(bot):
    cog = HotReload(bot)
    await bot.add_cog(cog)
