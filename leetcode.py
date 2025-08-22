import os, requests
import pytz

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

import discord
from discord.ext import commands

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler(timezone=pytz.timezone("America/New_York"))

def get_daily_question() -> str:
    graphql_query = {
        "query": """
            query {
                activeDailyCodingChallengeQuestion {
                    date
                    link
                    question {
                        acRate
                        difficulty
                        questionFrontendId
                        title
                        topicTags {
                            name
                        }
                    }
                }
            }
        """
    }
    res = requests.post(url="https://leetcode.com/graphql", json=graphql_query, headers={"Content-Type": "application/json"})
    data = res.json()["data"]["activeDailyCodingChallengeQuestion"]
    question_data = data['question']
    
    message =  f"""Daily Question for {data['date']}
[{question_data['questionFrontendId']}. {question_data['title']} ({question_data['difficulty']} {round(question_data['acRate'], 2)}%)](https://leetcode.com{data['link']}description/?envType=daily-question&envId={data['date']}) 

Topics: ||{", ".join(topicTag["name"] for topicTag in question_data['topicTags'])}||
"""
    return message

async def send_message(channel_id: int, message: str = get_daily_question()):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(message)
    else:
        print(f"Channel {channel_id} not found")

@bot.event
async def on_ready():
    await send_message(CHANNEL_ID)
    scheduler.add_job(send_message, CronTrigger(hour=8, minute=0), args=[CHANNEL_ID])
    scheduler.start()

# TODO: command to join leetcoder role and keep score, etc.
bot.run(DISCORD_TOKEN)