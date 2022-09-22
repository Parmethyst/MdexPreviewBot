import discord
from discord import app_commands
from discord.ext import commands
import time
import json
import requests
import re


class dynasty_module(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
      self.bot = bot
      super().__init__()  # this is now required in this context.

  @app_commands.command(name="ds", description="Command to preview dynasty-scans link")
  async def dynasty(self, interaction: discord.Interaction,
    link: str) -> None:
      """ /commands1 """
      link = link.lower()
      ts = time.localtime()
      timeString=time.strftime("%Y-%m-%d %H:%M:%S", ts)
      print(f"[{timeString} | {interaction.user}]: {link}")
      if link=="help":
        print("Usage help successfully sent")
        await interaction.response.send_message(content=f"Usage: /ds [dynasty-scans link without the brackets]",ephemeral=True)
        return
      if not re.match(r"(https:\/\/dynasty-scans.com\/)(series|anthologies|issues|chapters)\/([a-z\-0-9\-_])+", link):
        print("Not a dynasty-scans link!")
        await interaction.response.send_message('dynasty-scans link malformed! If this is not a typo please contact Parmethyst#7954.',ephemeral=True)
        return

      await interaction.response.defer(ephemeral=False)
      
      if link[-1]=='/': #if last character of link is slash then remove slash
        link=link[:-1]

      split_link=link.rsplit('/',2)[1:] #split link to parts divided by '/' character
      # print(split_link)
      if split_link[0]=="chapters":
        is_nsfw=False
        #print(split_link)
        requested_page=1
        chapter_permalink=""
        if re.match(r"([a-z\-0-9\-_])+#([0-9])+", split_link[1]):
            chapter_split=split_link[1].split('#')
            #print(chapter_split) 
            chapter_permalink=chapter_split[0]
            #print(chapter_permalink)
            requested_page=int(chapter_split[1])
            #print(requested_page)
            if(requested_page<1): requested_page=1
        else:
            chapter_permalink=split_link[1]
        json_link=f"https://dynasty-scans.com/chapters/{chapter_permalink}.json"
        response = requests.get(f"{json_link}")
        json_data = json.loads(response.text)
        # print(json_data)
        if requested_page >= len(json_data["pages"]):
            requested_page=len(json_data["pages"])
        title=json_data["title"]
        tags=json_data["tags"]
        for tag in tags:
            if tag["name"]=="NSFW":
                is_nsfw=True  
            if tag["type"]=="Anthology" or tag["type"]=="Issue":
                title=f"{json_data['title']} ({tag['name']})"
            elif tag["type"]=="Doujin":
                title=f"{json_data['title']} (Parody: {tag['name']})"
        page_image=json_data["pages"][requested_page-1]["url"]
        embed=discord.Embed(
            title=f"{title}",
            url=f"{link}")
        if not is_nsfw:
          embed.add_field(name="Preview doesn't load?", value=f"[https://dynasty-scans.com{page_image}](https://dynasty-scans.com{page_image})")
          embed.set_image(url=f"https://dynasty-scans.com{page_image}")
        elif is_nsfw:
          embed.add_field(name="NSFW chapter, no preview.", value=f"[https://dynasty-scans.com{page_image}](https://dynasty-scans.com{page_image})")
        # embed.set_author(
        #     name=ctx.author.display_name,
        #     icon_url=ctx.author.avatar_url)
        embed.set_footer(text="Code: https://github.com/Parmethyst/MdexPreviewBot")
        print(f"{title}")
        await interaction.followup.send(embed=embed)

      elif split_link[0]=="series" or split_link[0]=="anthologies" or split_link[0]=="issues":
        is_nsfw=False
        is_tags=False
        is_cover=True
        response = requests.get(f"{link}.json")
        json_data = json.loads(response.text)
        # print(json_data)
        title=json_data["name"]
        description=""
        if json_data["description"] is None:
            description=""
        else:
            description=json_data["description"]
        cover_url=""
        cover_link=""
        if json_data['cover'] is None:
            is_cover=False
        else:
            cover_url=json_data['cover'].partition("?")
            cover_link=f"https://dynasty-scans.com{cover_url[0]}"
            is_cover=True

        tags=json_data["tags"]
        tags.sort(key=lambda x: x["type"], reverse=False)
        tag_list=list()
        for tag in tags:
            is_tags=True
            tag_list.append(tag["name"])
            if tag["name"]=="NSFW":
                is_nsfw=True
        tag_string=", ".join(tag_list)
        embed=discord.Embed(  
            title=f"{title}",
            url=f"{link}",
            description=f"{description}")
        if is_tags: embed.add_field(name="Tags", value=f"{tag_string}")
        # embed.set_author(
        #     name=ctx.author.display_name,
        #     icon_url=ctx.author.avatar_url)
        if is_cover:
            if not is_nsfw:
                embed.set_image(url=f"{cover_link}")
            # elif is_nsfw and ctx.channel.is_nsfw():
            #     embed.set_image(url=f"{cover_link}")
        embed.set_footer(text="Code: https://github.com/Parmethyst/MdexPreviewBot")
        print(f"{title}")
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(dynasty_module(bot))