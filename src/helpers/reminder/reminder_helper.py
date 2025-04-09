from helpers.nullbot_helper import *
from db.nullbot_db_helper import *

async def remind(ctx, *args):
    """
    Create a reminder for the user in the current channel.
    """
    usage = ("*null remind [time] [date (optional)] [reminder]*\n\n"
             "Usage: NullBot will ping you at the specified time (24h format, EST) and date with the reminder message.\n\n"
             "Accepted date formats: *YYYY-MM-dd* or *MM-dd-yyyy* (may substitute dashes with slashes)\n"
             "Accepted time formats: *HH:mm* or *HH:mm:ss*")
    if(len(args) >= 2):
        time_string = args[0]
        date_string = args[1]
        time = validate_time(time_string)
        date = validate_date(date_string)
        bot_response = None
        reminder_text = None
        if(time is not None):
            if(date is not None):
                if len(args) > 2:
                    reminder_text = ' '.join(args[2:])
                    bot_response = "I'll remind you to \"" + reminder_text + "\" at " + time_string + " on " + date_string
                else:
                    await ctx.send("No reminder message provided")
            else:
                reminder_text = ' '.join(args[1:])
                bot_response = "I'll remind you to \"" + reminder_text + "\" at " + time_string
        else:
            await ctx.send("Time must to be in the correct format (Type *null remind* for help)")
        if(reminder_text is not None):
            user_id = create_user(ctx.author.name, ctx.author.id)
            if(user_id is not None):
                context_id = create_context(user_id, ctx.guild.id, ctx.channel.id)
                if(context_id is not None):
                    if(date is None):
                        date = datetime.strftime(datetime.now(), "%Y-%m-%d")
                    datetime_string = date + " " + time
                    reminder_id = create_reminder(reminder_text, datetime_string, context_id)
                    if(reminder_id is not None):
                        await ctx.send(bot_response)
                else:
                    await ctx.send("Failed to create context row for user_id = " + str(user_id))
            else:
                await ctx.send("Failed to create users row for Discord ID " + str(ctx.author.id))
    else:
        await ctx.send(usage)

async def showReminders(ctx):
    """
    Show all reminders for the user in the current channel.
    """
    reminder_list = get_all_reminders()
    index = 1
    bot_response = ""
    for reminder in reminder_list:
        bot_response += str(index) + ". Remind " + reminder.context.user.user_name + " to \"" + reminder.reminder_text + "\" on " + str(reminder.reminder_date) + "\n"
        index += 1
    await ctx.send(bot_response)

async def checkReminders(ctx, bot):
    """
    Check all reminders for the user in the current channel.
    """
    reminder_list = get_all_reminders(ctx.channel.id)
    now = datetime.now()

    if(reminder_list is not None and len(reminder_list) > 0):
        for reminder in reminder_list:
            guild = bot.get_guild(reminder.context.guild_id)
            channel = guild.get_channel(reminder.context.channel_id)
            if(reminder.reminder_date < now):
                await channel.send(f"<@{reminder.context.user.discord_id}>, reminder to \"{reminder.reminder_text}\"")
                delete_reminder(reminder.reminder_id)
                delete_context(reminder.context.context_id)
            else:
                #await channel.send("I will remind " + str(reminder.context.user.user_name) + " to \"" + reminder.reminder_text + "\" on " + str(reminder.reminder_date))
                await channel.send("I will remind " + f"<@{reminder.context.user.user_name}> to \"{reminder.reminder_text}\" on \" {reminder.reminder_date}\"") 
    else:
        await ctx.send("There are no pending reminders")