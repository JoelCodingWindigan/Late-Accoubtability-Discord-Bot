import discord
from discord.ext import commands
from matcher import *

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

# hashmap used to keep track of how often a user says they are late or something similar 
my_hashmap = {}


@client.event
async def on_ready():
    print("The Bot is now ready for use! Booyah")
    


@client.event
async def on_message(message):
    #print(f"Message receoved: {message.content}")
    await count_message(message)
    await client.process_commands(message)


async def count_message(message):
    target_phrase = "I'll be late"
    user_input = message.content.lower()

    # Check similarity using Levenshtein distance
    similarity = default_similarity(user_input, target_phrase)

    # Define a threshold for considering a match
    similarity_threshold = 0.8

    if similarity >= similarity_threshold:
        user_id = str(message.author.id)

        # Increment the count for the user or set it to 1 if it doesn't exist
        my_hashmap[user_id] = my_hashmap.get(user_id, 0) + 1
        #print("Bro fr you gonna be late again!? You've been late " + str(my_hashmap[user_id]) + "times. ")
        await message.channel.send("bro fr?? you gonna be late again?! You've been late " + str(my_hashmap[user_id]) + " times.")

@client.command()
async def print_count(ctx):
    user_id = str(ctx.author.id)
    count = my_hashmap.get(user_id, 0)
    await ctx.send(f'This user {ctx.author.name} has been late {count} times')


client.run('MTIwMzA5NDQ0OTYxMDI5MzM1MA.Grgane.jEi-h9LUT838kSBOZEO8ip2Kj7owXQTLzS7eXI')



# Run the bot