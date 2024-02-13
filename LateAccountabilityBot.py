import discord
from discord.ext import commands
import openai
import asyncio

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
openai.api_key = 'API token'

openai.base_url = "https://api.openai.com/v1/"
openai.default_headers = {"x-foo": "true"}



# hashmap used to keep track of how often a user says they are late or something similar 
my_hashmap = {}


@client.event
async def on_ready():
    print("The Bot is now ready for use! Booyah")


@client.event
async def on_message(message):
    await count_message(message)
    await client.process_commands(message)


async def count_message(message):
    user_input = message.content.lower()

    # Check if the word "late" is present in the message
    
    is_late = await gpt3_check_late(user_input)
    
    if not message.author.bot:
        if is_late:
            user_id = str(message.author.id)
            my_hashmap[user_id] = my_hashmap.get(user_id, 0) + 1
            await message.channel.send(f" You've been late {my_hashmap[user_id]} time(s).")


async def gpt3_check_late(user_input):
    # Define the prompt for GPT-3
    prompt = f"The user said: {user_input}. Is the user indicating that they will be late?"

    
    # Introduce a delay to avoid rate limits
    await asyncio.sleep(2)  # 2 seconds delay

        # Request completion from GPT-3 using the chat endpoint
    completion = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": prompt,
            
        },
    ],
    )
    generated_text = completion.choices[0].message.content

        # Determine if the generated text indicates the user will be late
    is_late = "yes" in generated_text.lower()  # Adjust as needed

    return is_late

    

@client.command()
async def print_count(ctx):
    user_id = str(ctx.author.id)
    count = my_hashmap.get(user_id, 0)
    await ctx.send(f'This user {ctx.author.name} has been late {count} times')




client.run('bot token')
