# bot.py
import os
import discord
import asyncio
import typing
from typing import *
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

client = commands.Bot(command_prefix='$', intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def close():
    print("Shutting down...")
    pass

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$try_sync') and message.guild.id==286355885389774868:
        guild = discord.Object(id=286355885389774868)
        client.tree.copy_global_to(guild=guild)
        await client.tree.sync()
        await message.channel.send("SYNC")


@client.command(name="sync") #NOT WORKING BUT INTERESTING
@commands.guild_only()
async def sync(
        ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    print("ENTER")
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


# Works like:
# !sync -> global sync
# !sync ~ -> sync current guild
# !sync * -> copies all global app commands to current guild and syncs
# !sync ^ -> clears all commands from the current guild target and syncs (removes guild commands)
# !sync id_1 id_2 -> syncs guilds with id 1 and 2


async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')


async def main():
    await load()
    async with client:
        await client.start(TOKEN)


async def shutdown_handler():
    await client.close()



try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
finally:
    print("Shutting down...")
