# bot.py
import os
import requests
import discord
import json
from dotenv import load_dotenv
from discord_slash import SlashCommand
from discord.ext import commands
from discord_slash.utils.manage_commands import create_option

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix = 'md.')
slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_slash_command_error(ctx, error):

    if isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.send('You do not have permission to execute this command', hidden=True)

    else:
       await ctx.send('Oops! Something went wrong, please report to Parmethyst#7954 or try again.', hidden=True)
       raise error  # this will show some debug print in the console, when debugging

@slash.slash(name="ping")
async def _ping(ctx):
    await ctx.send(f"Pong! ({client.latency*1000}ms)")

@slash.slash(
    name="md",
    description="Command to preview a mangadex link",
    options=[
        create_option(
            name="link",
            description="Put your mangadex link here",
            option_type=3,
            required=False
        )
    ])
async def md(ctx, link="help"):
    print(f"{ctx.author.display_name}: {link}")
    if link[-1]=='/':
        link=link[:-1]
    split_link=link.rsplit('/',2)[1:]
    if link=="help":
        await ctx.send(content=f"Usage: /md [mangadex manga/chapter link without the brackets]")
    elif split_link[0]=="title":

        manga_id=split_link[1]
        response = requests.get(f"https://api.mangadex.org/manga/{manga_id}")
        json_data = json.loads(response.text)
        title=json_data["data"]["attributes"]["title"]["en"]
        description=json_data["data"]["attributes"]["description"]["en"]
        cover_id=""
        relationships=json_data["relationships"]

        for relation in relationships:
            if relation["type"]=="cover_art":
                cover_id=relation["id"]
                break

        response = requests.get(f"https://api.mangadex.org/cover/{cover_id}")
        json_data = json.loads(response.text)
        cover_filename=json_data["data"]["attributes"]["fileName"]

        embed=discord.Embed(
            title=f"{title}",
            url=f"{link}",
            description=f"{description}")

        embed.set_author(
            name=ctx.author.display_name, 
            icon_url=ctx.author.avatar_url)

        embed.set_image(url=f"https://uploads.mangadex.org/covers/{manga_id}/{cover_filename}")
        embed.set_footer(text="Open sourced https://github.com/Parmethyst/MdexPreviewBot")
        print(title)
        print("")
        await ctx.send(embed=embed)

    elif split_link[0]=="chapter":
        chapter_id=split_link[1]
        response = requests.get(f"https://api.mangadex.org/chapter/{chapter_id}")
        json_data=json.loads(response.text)
        chapter_hash=json_data["data"]["attributes"]["hash"]
        chapter_page=json_data["data"]["attributes"]["data"][0]
        chapter_number=json_data["data"]["attributes"]["chapter"]
        relationships=json_data["relationships"]
        response = requests.get(f"https://api.mangadex.org/at-home/server/{chapter_id}")
        json_data=json.loads(response.text)
        base_url=json_data["baseUrl"]

        manga_id=""
        for relation in relationships:
            if relation["type"]=="manga":
                manga_id=relation["id"]
                break

        response = requests.get(f"https://api.mangadex.org/manga/{manga_id}")
        json_data = json.loads(response.text)
        title=json_data["data"]["attributes"]["title"]["en"]

        embed=discord.Embed(
            title=f"{title} (Ch: {chapter_number})",
            url=f"{link}")
        embed.set_author(
            name=ctx.author.display_name, 
            icon_url=ctx.author.avatar_url)
        embed.set_image(url=f"{base_url}/data/{chapter_hash}/{chapter_page}")
        embed.set_footer(text="Open sourced https://github.com/Parmethyst/MdexPreviewBot")
        print(f"{title} (Ch: {chapter_number})")
        print("")
        await ctx.send(embed=embed)

    else:
        chapter_id=split_link[0]
        requested_page=int(split_link[1])

        if requested_page < 1:
            requested_page=0
        else:
            requested_page=int(split_link[1])-1

        response = requests.get(f"https://api.mangadex.org/chapter/{chapter_id}")
        json_data=json.loads(response.text)

        if requested_page >= len(json_data["data"]["attributes"]["data"]):
            requested_page=len(json_data["data"]["attributes"]["data"])-1
        
        chapter_hash=json_data["data"]["attributes"]["hash"]
        chapter_page=json_data["data"]["attributes"]["data"][requested_page]
        chapter_number=json_data["data"]["attributes"]["chapter"]
        relationships=json_data["relationships"]
        response = requests.get(f"https://api.mangadex.org/at-home/server/{chapter_id}")
        json_data=json.loads(response.text)
        base_url=json_data["baseUrl"]

        manga_id=""
        for relation in relationships:
            if relation["type"]=="manga":
                manga_id=relation["id"]
                break

        response = requests.get(f"https://api.mangadex.org/manga/{manga_id}")
        json_data = json.loads(response.text)
        title=json_data["data"]["attributes"]["title"]["en"]

        embed=discord.Embed(
            title=f"{title} (Ch: {chapter_number})",
            url=f"{link}")
        embed.set_author(
            name=ctx.author.display_name, 
            icon_url=ctx.author.avatar_url)
        embed.set_image(url=f"{base_url}/data/{chapter_hash}/{chapter_page}")
        embed.set_footer(text="Open sourced https://github.com/Parmethyst/MdexPreviewBot")
        print(f"{title} (Ch: {chapter_number})")
        print("")
        await ctx.send(embed=embed)

client.run(TOKEN)