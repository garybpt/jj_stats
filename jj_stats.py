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
async def update_stats(ctx):
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild is not None:
        verified_role_id = int(os.getenv("VERIFIED_ROLE_ID"))
        verified_role = discord.utils.get(guild.roles, id=verified_role_id)

        subscriber_role_id = int(os.getenv("SUBSCRIBER_ROLE_ID"))  # Replace with your subscriber role ID
        subscriber_role = discord.utils.get(guild.roles, id=subscriber_role_id)

        if verified_role is not None and subscriber_role is not None:
            verified_members = [member for member in guild.members if verified_role in member.roles]
            subscriber_members = [member for member in guild.members if subscriber_role in member.roles]

            verified_count = len(verified_members)
            subscriber_count = len(subscriber_members)
            conversion_rate = (subscriber_count / verified_count) * 100 if verified_count > 0 else 0

            # Load existing data or create an empty list
            try:
                with open("jj_stats.json", "r") as json_file:
                    data = json.load(json_file)
            except (json.JSONDecodeError, FileNotFoundError):
                data = []

            # Append new counts, totals, and conversion rate to the list with current date
            new_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "verified_count": verified_count,
                "total_verified_users": sum(entry["verified_count"] for entry in data) + verified_count,
                "subscriber_count": subscriber_count,
                "total_subscribers": sum(entry["subscriber_count"] for entry in data) + subscriber_count,
                "conversion_rate": conversion_rate
            }
            data.insert(0, new_entry)

            # Save the entire list to JSON file
            with open("jj_stats.json", "w") as json_file:
                json.dump(data, json_file, indent=2)

            print(f"Stats updated - Verified users: {verified_count}, Subscribers: {subscriber_count}, Conversion Rate: {conversion_rate:.2f}%. Stats saved to jj_stats.json")

            # Optionally, log the entry to Discord
            await ctx.send(f"Stats updated: {new_entry}")
        else:
            await ctx.send("Roles not found. Make sure 'verified' and 'subscriber' roles are correctly set.")
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