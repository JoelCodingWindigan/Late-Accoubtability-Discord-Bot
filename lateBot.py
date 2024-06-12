import sqlite3
import discord 
from discord.ext import commands

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

# Connect to the SQLite database
sqliteConnection = sqlite3.connect('backup.db')
cursor = sqliteConnection.cursor()

# Create the USER table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS USER (
                    DISCORDID TEXT PRIMARY KEY,
                    COUNTER INTEGER
                )''')

# Load user data from the database into a dictionary
def load_user_data():
    user_data = {}
    cursor.execute("SELECT DISCORDID, COUNTER FROM USER")
    rows = cursor.fetchall()
    for row in rows:
        user_data[row[0]] = row[1]
    return user_data

# Save user data to the database
def save_user_data(user_data):
    cursor.execute("DELETE FROM USER")
    for user_id, count in user_data.items():
        cursor.execute("INSERT INTO USER (DISCORDID, COUNTER) VALUES (?, ?)", (user_id, count))
    sqliteConnection.commit()

# Initialize the user data dictionary
my_hashmap = load_user_data()

# List of phrases used to detect late mentions
phrases = ["i'll be late", "i'm going to be late", "i'll be there in 15 minutes", "be there late"]

@client.event
async def on_ready():
    print("The Bot is online")
    

@client.event
async def on_message(message):
    if not message.author.bot:
        await count_message(message)
    await client.process_commands(message)

async def count_message(message):
    user_input = message.content.lower()
    user_id = str(message.author.id)
    for phrase in phrases:
        if levenshtein_distance(user_input, phrase) <= 3:
            if user_id in my_hashmap:
                my_hashmap[user_id] += 1
            else:
                my_hashmap[user_id] = 1
            save_user_data(my_hashmap)  # Update the database
            break

@client.command()
async def print_count(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author
    user_id = str(user.id)
    count = my_hashmap.get(user_id, 0)
    await ctx.send(f'This user {user.name} said they are going to be late {count} times')

@client.command()
async def decrement(ctx, user: discord.User = None):
    if check_role(ctx, 'accountant'):
        if user is None:
            user = ctx.author
        user_id = str(user.id)
        if user_id in my_hashmap and my_hashmap[user_id] > 0:
            my_hashmap[user_id] -= 1
            save_user_data(my_hashmap)  # Update the database
            await ctx.send(f'{user.name}\'s late counter has been decremented')
        else:
            await ctx.send(f'{user.name} does not have any late count to decrement')
    else:
        await ctx.send('Sorry, you are not an accountant')

@client.command()
async def increment(ctx, user: discord.User = None):
    if check_role(ctx, 'accountant'):
        if user is None:
            user = ctx.author
        user_id = str(user.id)
        if user_id in my_hashmap:
            my_hashmap[user_id] += 1
        else:
            my_hashmap[user_id] = 1
        save_user_data(my_hashmap)  # Update the database
        await ctx.send(f'{user.name}\'s late counter has been incremented')
    else:
        await ctx.send('Sorry, you are not an accountant')

def check_role(ctx, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    return role in ctx.author.roles

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]




client.run('MTIwMzA5NDQ0OTYxMDI5MzM1MA.GGW9eo.RAQVCq1LLquzWXUufqtTKO-TjlQ8mJKbBMfCL0')