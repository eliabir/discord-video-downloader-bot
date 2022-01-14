#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from pytube import YouTube

# Local functions
from gofile_upload import upload_gofile
from imgur_upload import upload_imgur

# Loads API keys from environment variables
load_dotenv()

# Grabs the API keys loaded into environment variables
DISCORD_API = os.environ.get("DISCORD_API")
IMGUR_API_ID = os.environ.get("IMGUR_API_ID")
IMGUR_API_SECRET = os.environ.get("IMGUR_API_SECRET")

# Paths
vid_path = "/usr/src/bot/videos"  # The path to the video storage directory in the Docker container
#vid_path = "/home/dockerm1/discord_dl_bot/videos"  # The path to the video storage directory on the local machine
os.chdir(vid_path)  # Changes directory to the video storage directory

# Variants of the YouTube video url to verify YouTube links
yt_url_variants = ["youtube.com", "youtu.be"]

# Sets the prefix for bot commands
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')  # Removes the default help command to be able to make our own


# Function for switching spaces to underscores in file names to make them more manageable
def create_file_name(raw_filename):
    new_filename = raw_filename.replace(" ", "_") + '.mp4'
    return new_filename


# The event that triggers when the bot logs into a server
@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))


# The bot help command triggered by !help
@bot.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(
        title = 'Video Downloader Bot',
        description = 'A bot that downloads the provided YouTube video and uploads it either directly to Discord, to Imgur or to Gofile depending om the file size.',
        color = discord.Colour.blue()
    )

    embed.add_field(name='!dl <URL>', value='Downloads YouTube video from given URL', inline=False)

    await ctx.send(embed=embed)


# The main command for downloading YouTube videos
@bot.command()
async def dl(ctx, url):
    if any(x in url for x in yt_url_variants):  # Checks if the given URL contains the variants given in yt_url_variants
        vid = YouTube(url)  # Creates a YouTube API object
        
        videofile_name = create_file_name(vid.title)  # Grabs the video title to use for the file name
        message = await ctx.send(f"Downloading '{vid.title}'...")
        
        # Checks the video streams and filters only streams using the progressive technique because the file contains both audio and video
        # The streams are ordered by descending quality and the first (best quality) stream is downloaded
        vid.streams \
            .filter(progressive=True) \
            .order_by('resolution') \
            .desc() \
            .first() \
            .download(filename=videofile_name)
        
        await message.edit(content=f"Downloaded '{vid.title}'! Uploading...")
        
        filesize = os.path.getsize(videofile_name)  # Gets size of video file
        
        # Checks if filesize is smaller than Discord file upload limit (8MB)
        if filesize < 8000000:
            await message.edit(content=vid.title)
            await ctx.send(file=discord.File(videofile_name))  # Uploads the file directly to discord

            link = upload_gofile(videofile_name, vid_path)  # Also uploads the file to gofile
            await ctx.send(f"Also uploaded to Gofile: \n{link}")

        # Checks if filsize is smaller than Imgur file upload limit (1GB)
        elif 8000000 < filesize < 1000000000:
            await message.edit(content='Uploading to Imgur...')
            imgur_url = upload_imgur(videofile_name, vid_path, IMGUR_API_ID, IMGUR_API_SECRET)  # Uploads file to imgur 

            await message.edit(content=imgur_url)

            link = upload_gofile(videofile_name, vid_path)  # Also uploads the file to gofile
            await ctx.send(f"Also uploaded to Gofile: \n{link}")

        # Checks if file is bigger than both Discord and Imgur file upload limit
        elif filesize > 1000000000:
            link = upload_gofile(videofile_name, vid_path)  # Uploads file to gofile
            await message.edit(content=f"Download '{videofile_name}' here: \n{link}")

        else:
            await ctx.send("RIP")
        
        # Removes video file from local storage
        print('Videofile removed from videos/ folder')
        os.remove(videofile_name)

    # Alerts user if a non YouTube link is provided
    else:
        print("Non YouTube link passed")
        await ctx.send(f"'{url} does not seem to be a YouTube link")


# Starts the Discord bot
bot.run(DISCORD_API)
