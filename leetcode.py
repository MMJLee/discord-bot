import datetime
from zoneinfo import ZoneInfo
import requests
import discord
from discord.ext import commands, tasks

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
# Schedule time: 08:00 EST
time_to_run = datetime.time(hour=8, minute=0, tzinfo=ZoneInfo("America/New_York"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

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

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_leetcode.start()

    def cog_unload(self):
        self.daily_leetcode.cancel()

    @tasks.loop(time=time_to_run)
    async def daily_leetcode(self):
        channel = self.bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(get_daily_question())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    if not any(isinstance(c, MyCog) for c in bot.cogs.values()):
        await bot.add_cog(MyCog(bot))

bot.run(DISCORD_TOKEN)
