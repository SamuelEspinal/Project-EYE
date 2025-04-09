import random
import json
import os
from collections import Counter
from datetime import datetime, date
import discord
from discord.ext import commands

#### Nulldle Game Helper ####
GAMES_FILE = "src\\helpers\\games\\nulldle\\active_games.json"
STATS_FILE = "src\\helpers\\games\\nulldle\\nulldle_stats.json"
DAILY_FILE = "src\\helpers\\games\\nulldle\\daily_word.json"
wordFilePath = "src\\helpers\\games\\nulldle\\words.txt"

# Load word list
with open(wordFilePath, "r") as f:
    WORD_LIST = [line.strip().lower() for line in f if len(line.strip()) == 5]

# Load saved games if available
try:
    if os.path.exists(GAMES_FILE):
        with open(GAMES_FILE, "r") as f:
            active_games = json.load(f)
            active_games = {int(k): v for k, v in active_games.items()}
    else:
        raise FileNotFoundError
except (json.JSONDecodeError, FileNotFoundError):
    active_games = {}

# Load win/loss stats if available
try:
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            user_stats = json.load(f)
            user_stats = {int(k): v for k, v in user_stats.items()}
    else:
        raise FileNotFoundError
except (json.JSONDecodeError, FileNotFoundError):
    user_stats = {}

# Load or set today's daily word
if os.path.exists(DAILY_FILE):
    with open(DAILY_FILE, "r") as f:
        daily_data = json.load(f)
else:
    daily_data = {"date": None, "word": None, "guessed_users": []}

if daily_data["date"] != date.today().isoformat():
    daily_data = {
        "date": date.today().isoformat(),
        "word": random.choice(WORD_LIST),
        "guessed_users": []
    }
    with open(DAILY_FILE, "w") as f:
        json.dump(daily_data, f)

#### Save current game state to file ####
def save_games():
    with open(GAMES_FILE, "w") as f:
        json.dump(active_games, f)

#### Save win/loss stats ####
def save_stats():
    with open(STATS_FILE, "w") as f:
        json.dump(user_stats, f)

#### Save daily challenge state ####
def save_daily():
    with open(DAILY_FILE, "w") as f:
        json.dump(daily_data, f)

#### Emoji feedback generator ####
def get_nulldle_feedback(guess, target):
    feedback = []
    used_letters = list(target)

    for i, char in enumerate(guess):
        if char == target[i]:
            feedback.append("🟩")  # Green
            used_letters[i] = None
        else:
            feedback.append(None)

    for i, char in enumerate(guess):
        if feedback[i] is None:
            if char in used_letters:
                feedback[i] = "🟨"  # Yellow
                used_letters[used_letters.index(char)] = None
            else:
                feedback[i] = "⬜"  # Gray

    return "".join(feedback)
#### Nulldle help command ####
async def nulldle_help(ctx):
    embed = discord.Embed(
        title="🎮 Nulldle Command Guide",
        description="Welcome to **Nulldle**, the daily Wordle-style game on Discord!",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🟨 `null playnulldle`",
        value="Start a **normal Nulldle game**. Guess a random 5-letter word with up to 6 tries.",
        inline=False
    )
    embed.add_field(
        name="📅 `null nulldle daily`",
        value="Play the **daily challenge** — one word shared by all players each day. Can only be attempted once!",
        inline=False
    )
    embed.add_field(
        name="📊 `null nulldle leaderboard`",
        value="View the **global leaderboard**. See who has the most wins, best streaks, and fewest losses. \nType `null nulldle leaderboard [streak/daily]` to sort by streak or daily wins.",
        inline=False
    )
    embed.add_field(
        name="📈 `null nulldle stats`",
        value="Check your **personal stats** including wins, daily wins, losses, current streak, and best streak.",
        inline=False
    )
    await ctx.send(embed=embed)
#### Start a regular Nulldle game ####
async def start_nulldle(ctx):
    user_id = ctx.author.id

    if user_id in active_games:
        await ctx.send("You already have a game in progress! Use `null guess [word]`.")
        return

    word = random.choice(WORD_LIST)
    active_games[user_id] = {"word": word, "guesses": [], "daily": False}
    save_games()
    await ctx.send("🟨 Nulldle started! Guess the 5-letter word using `null guess [word]`. You have 6 tries.")

#### Show leaderboard ####
async def show_nulldle_leaderboard(ctx, sort_by: str = "wins", show_all: bool = False, daily_only: bool = False):
    if not user_stats:
        await ctx.send("No Nulldle games have been completed yet.")
        return

    valid_sort_keys = {
        "wins": lambda x: (x[1]["wins"], x[1].get("max_streak", 0)),
        "streak": lambda x: (x[1].get("streak", 0), x[1]["wins"]),
        "daily": lambda x: (x[1].get("daily_wins", 0), x[1]["wins"])
    }

    sort_func = valid_sort_keys.get(sort_by.lower(), valid_sort_keys["wins"])
    if daily_only:
        filtered_stats = filter(lambda x: x[1].get("daily_wins", 0) > 0 or show_all, user_stats.items())
    else:
        filtered_stats = user_stats.items() if show_all else filter(lambda x: x[1].get("wins", 0) > 0, user_stats.items())

    leaderboard = sorted(filtered_stats, key=sort_func, reverse=True)
    embed = discord.Embed(title="📊 Nulldle Leaderboard", color=discord.Color.green())

    for uid, stats in leaderboard[:10]:
        try:
            member = await ctx.guild.fetch_member(uid) if ctx.guild else None
            name = member.display_name if member else f"<@{uid}>"
        except:
            name = f"<@{uid}>"

        embed.add_field(
            name=name,
            value=(
                f"🏆 Wins: {stats['wins']}\n"
                f"📅 Daily Wins: {stats.get('daily_wins', 0)}\n"
                f"❌ Losses: {stats['losses']}\n"
                f"🔥 Streak: {stats.get('streak', 0)}\n"
                f"🔝 Max Streak: {stats.get('max_streak', 0)}\n"
            ),
            inline=False
        )

    await ctx.send(embed=embed)

#### Process a guess ####
async def make_nulldle_guess(ctx, word):
    user_id = ctx.author.id
    word = word.lower()

    if user_id not in active_games:
        await ctx.send("You don't have a Nulldle game in progress. Start one with `null playnulldle` or `null nulldle daily`.")
        return

    if len(word) != 5 or word not in WORD_LIST:
        await ctx.send("❌ Invalid word. Make sure it's 5 letters and on the word list.")
        return

    game = active_games[user_id]
    feedback = get_nulldle_feedback(word, game["word"])
    game["guesses"].append((word, feedback))

    guess_block = "\n".join([f"`{g.upper()}` {f}" for g, f in game["guesses"]])

    if game.get("daily", False):
        try:
            await ctx.author.send(f"📬 Your Nulldle Daily Guess:```{len(game['guesses'])}/6 attempts```{guess_block}")
            await ctx.send("✅ Guess received! Check your DMs for feedback.")
        except discord.Forbidden:
            await ctx.send("❌ I can't DM you! Please enable DMs to play the daily challenge.")
    else:
        await ctx.send(f"```{len(game['guesses'])}/6 attempts```{guess_block}")

    if word == game["word"]:
        is_daily = game.get("daily", False)
        if is_daily:
            await ctx.send("🎉 You completed today's Nulldle challenge!")
            if user_id not in daily_data["guessed_users"]:
                daily_data["guessed_users"].append(user_id)
                save_daily()
        else:
            await ctx.send(f"🎉 You guessed it! The word was **{game['word'].upper()}**.")

        del active_games[user_id]
        stats = user_stats.setdefault(user_id, {"wins": 0, "losses": 0, "streak": 0, "max_streak": 0, "last_win_date": None, "daily_wins": 0})
        stats["wins"] += 1
        if is_daily:
            stats["daily_wins"] = stats.get("daily_wins", 0) + 1

        today = date.today()
        yesterday = today.replace(day=today.day - 1)
        today_iso = today.isoformat()
        yesterday_iso = yesterday.isoformat()

        if stats["last_win_date"] == today_iso:
            pass  # already counted today — don't update streak again
        elif stats["last_win_date"] == yesterday_iso:
            stats["streak"] += 1
        else:
            stats["streak"] = 1

        stats["max_streak"] = max(stats["max_streak"], stats["streak"])
        stats["last_win_date"] = today_iso

        # TODO HERE BELOW get the ability to assign roles to users based on their streaks working 
        '''
        #  🎖️ Role rewards based on streak
        role_rewards = [
            (15, "Nulldle Champion"),
            (10, "Word Wizard"),
            (5, "Puzzle Master")
        ]

        if ctx.guild:
            member = ctx.guild.get_member(user_id)
            if member:
                # Remove all tracked roles first
                existing_roles = [discord.utils.get(ctx.guild.roles, name=rname) for _, rname in role_rewards]
                for r in existing_roles:
                    if r and r in member.roles:
                        await member.remove_roles(r)

                # Assign highest unlocked role
                for threshold, role_name in role_rewards:
                    if stats["streak"] >= threshold:
                        role = discord.utils.get(ctx.guild.roles, name=role_name)
                        if not role:
                            try:
                                role = await ctx.guild.create_role(name=role_name, reason="Nulldle streak reward")
                            except discord.Forbidden:
                                await ctx.send(f"⚠️ I don't have permission to create the '{role_name}' role.")
                                break

                        await member.add_roles(role)
                        await ctx.send(f"🏅 {member.mention} has reached a {stats['streak']}-win streak and earned the **{role_name}** title!")
                        break
    '''

    elif len(game["guesses"]) >= 6:
        is_daily = game.get("daily", False)
        if is_daily:
            await ctx.send("❌ You're out of guesses! Better luck tomorrow.")
            if user_id not in daily_data["guessed_users"]:
                daily_data["guessed_users"].append(user_id)
                save_daily()
        else:
            await ctx.send(f"❌ Out of guesses! The word was **{game['word'].upper()}**.")

        del active_games[user_id]
        stats = user_stats.setdefault(user_id, {"wins": 0, "losses": 0, "streak": 0, "max_streak": 0, "last_win_date": None})
        stats["losses"] += 1
        stats["streak"] = 0

    save_games()
    save_stats()

#### Start a daily challenge ####
async def daily_nulldle(ctx):
    user_id = ctx.author.id

    if user_id in daily_data["guessed_users"]:
        await ctx.send("🗓️ You've already completed today's Nulldle challenge!")
        return

    active_games[user_id] = {"word": daily_data["word"], "guesses": [], "daily": True}
    save_games()

    try:
        await ctx.author.send("🟦 **Daily Nulldle Challenge Started!**Guess the 5-letter word using `null guess [word]`. You have 6 tries. I'll send feedback here.")
        await ctx.send("📬 Daily Nulldle started! Check your DMs to continue guessing.")
    except discord.Forbidden:
        await ctx.send("❌ I can't DM you! Please enable DMs to play the daily challenge.")   

#### Show personal stats ####
async def nulldle_stats(ctx):
    user_id = ctx.author.id
    stats = user_stats.get(user_id)

    if not stats:
        await ctx.send("No stats found. Play some Nulldle games to get started!")
        return

    embed = discord.Embed(title=f"📈 Stats for {ctx.author.display_name}", color=discord.Color.gold())
    embed.add_field(name="🏆 Wins", value=str(stats.get("wins", 0)), inline=True)
    embed.add_field(name="📅 Daily Wins", value=str(stats.get("daily_wins", 0)), inline=True)
    embed.add_field(name="❌ Losses", value=str(stats.get("losses", 0)), inline=True)
    embed.add_field(name="🔥 Streak", value=str(stats.get("streak", 0)), inline=True)
    embed.add_field(name="🔝 Max Streak", value=str(stats.get("max_streak", 0)), inline=True)
    await ctx.send(embed=embed)
