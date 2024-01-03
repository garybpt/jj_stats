import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import os
import schedule
import time
from datetime import datetime, timedelta

# Load variables from .env file
load_dotenv()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user.name}")

@bot.command()
async def verified_count(ctx):
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild is not None:
        verified_role_id = int(os.getenv("VERIFIED_ROLE_ID"))
        verified_role = discord.utils.get(guild.roles, id=verified_role_id)

        if verified_role is not None:
            verified_members = [member for member in guild.members if verified_role in member.roles]
            count = len(verified_members)

            # Load existing data or create an empty list
            try:
                with open("jj_stats.json", "r") as json_file:
                    data = json.load(json_file)
            except (json.JSONDecodeError, FileNotFoundError):
                data = []

            # Append new count to the list with current date
            data.insert(0, {"timestamp": datetime.utcnow().isoformat(), "verified_count": count})

            # Save the entire list to JSON file
            with open("jj_stats.json", "w") as json_file:
                json.dump(data, json_file, indent=2)

            await ctx.send(f"Number of members with 'verified' role (ID: {verified_role_id}): {count}. Stats saved to jj_stats.json")
        else:
            await ctx.send(f"The 'verified' role with ID {verified_role_id} was not found.")
    else:
        await ctx.send("Bot is not in the specified server.")

def job():
    print("Running job...")
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    bot.run(os.getenv("BOT_TOKEN"))

# Schedule the job to run on the 1st of each month at 6:00 AM GMT
schedule.every().month.at("01:00").do(job)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)