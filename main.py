# bot.py
import os
import requests
import discord
import json
import re
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
       await ctx.send('Oops! Something went wrong, please try again or report to Parmethyst#7954 if the issue persists.', hidden=True)
       raise error  # this will show some debug print in the console, when debugging

@slash.slash(name="ping")
async def _ping(ctx):
    await ctx.send(f"Pong! ({client.latency*1000}ms)")

@slash.slash( #Make a slash command
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
async def md(ctx, link="help"): #Slash command function
    link=link.lower()
    print(f"{ctx.author.display_name}: {link}")

    if link=="help":
        print("Usage help successfully sent")
        print("")
        await ctx.send(content=f"Usage: /md [mangadex manga/chapter link without the brackets]")
        return
    if not re.match(r"(https:\/\/mangadex.org\/)(title|chapter)\/([a-z\-0-9])+", link):
        print("Not a mangadex link!")
        print("")
        await ctx.send('MangaDex link malformed! If this is not a typo please contact Parmethyst#7954.', hidden=True)
        return

    if link[-1]=='/': #if last character of link is slash then remove slash
        link=link[:-1]
    split_link=link.rsplit('/',2)[1:] #split link to parts divided by '/' character
    if split_link[0]=="title":

        manga_id=split_link[1]
        response = requests.get(f"https://api.mangadex.org/manga/{manga_id}")
        json_data = json.loads(response.text)
        title=get_suitable_title_language(json_data)
        description=json_data["data"]["attributes"]["description"]["en"]
        content_rating=json_data["data"]["attributes"]["contentRating"]
        if content_rating=="pornographic":
            title=f"{title} (NSFW)"
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
        if not content_rating=="pornographic":
            embed.set_image(url=f"https://uploads.mangadex.org/covers/{manga_id}/{cover_filename}")
        elif content_rating=="pornographic" and ctx.channel.is_nsfw():
            embed.set_image(url=f"https://uploads.mangadex.org/covers/{manga_id}/{cover_filename}")
        embed.set_footer(text="Code: https://github.com/Parmethyst/MdexPreviewBot")
        print(title)
        print("")
        await ctx.send(embed=embed)

    else:
        chapter_id=''
        requested_page=0
        if split_link[0]=="chapter":
            chapter_id=split_link[1]
        else:
            chapter_id=split_link[0]
            requested_page=int(split_link[1])

        if requested_page <= 0:
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
        title=get_suitable_title_language(json_data)

        embed=discord.Embed(
            title=f"{title} (Ch: {chapter_number})",
            url=f"{link}")
        embed.set_author(
            name=ctx.author.display_name, 
            icon_url=ctx.author.avatar_url)
        embed.set_image(url=f"{base_url}/data/{chapter_hash}/{chapter_page}")
        embed.set_footer(text="Code: https://github.com/Parmethyst/MdexPreviewBot")
        print(f"{title} (Ch: {chapter_number})")
        print("")
        await ctx.send(embed=embed)

def get_suitable_title_language(json_data):
    if "en" in json_data["data"]["attributes"]["title"]:
        return json_data["data"]["attributes"]["title"]["en"]
    elif "jp" in json_data["data"]["attributes"]["title"]:
        return json_data["data"]["attributes"]["title"]["jp"]
    elif "kr" in json_data["data"]["attributes"]["title"]:
        return json_data["data"]["attributes"]["title"]["kr"]
    elif "zh-hk" in json_data["data"]["attributes"]["title"]:
        return json_data["data"]["attributes"]["title"]["zh-hk"]
    elif "ru" in json_data["data"]["attributes"]["title"]:
        return json_data["data"]["attributes"]["title"]["ru"]
    else:
        return "N/A"

client.run(TOKEN)