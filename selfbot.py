"""
    Copyright (c) 2017 Gustavo Cortes
    
    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
# TODO: use cogs instead, only if adding more commands
import discord
import asyncio
import sys, getopt
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import logging
import traceback
import json
import os.path
from os import makedirs

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def invalid_token():
    print('Error: Must pass a token!')

def usage(prog):
    print('Usage: {} [-h|--help] {}{}'.format(prog,'--token=','<token>'))
    print('Or, place your token in \'settings.json\'!')

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.CRITICAL)
log = logging.getLogger()
log.setLevel(logging.INFO)
if not os.path.exists("logs"):
    os.makedirs("logs")
dt = datetime.now()
handler = logging.FileHandler(filename='./logs/selfbot.'+dt.strftime('%Y-%m-%d-%H%M%S.%f')+'.log', encoding='utf-8', mode='w')
dt = None
log.addHandler(handler)

token = None
bot = commands.Bot(command_prefix=['>'], description="Another selfbot made by a guy named Gustavo.", pm_help=None, help_attrs=dict(hidden=True), self_bot=True)

def log_message(message):
    if not isinstance(message, discord.Message):
        return
    # do we ignore bot chat?
    if bot.ignore_bot_chat and message.author.bot:
        return
    # do we ignore our own chat?
    if bot.ignore_own_messages and message.author.id == bot.user.id:
        return

    if message.embeds:
        # we have embeds; append those
        # we might have content (probably not though), but append just in case
        msg = ""
        if message.content.strip() != "":
            # only append message.content if there is anything to print
            msg = "\n" + message.content
        for embed in message.embeds:
            msg += "\n" + json.dumps(embed, indent=4)
    elif "\n" in message.content:
        # message is multiline; let's not make it "ugly" for the user in the log
        msg = "\n" + message.content
    else:
        msg = message.content

    # log ze message!
    log.info("[%s] %sChannel: %s, User: %s#%s(%s), Message: %s",
        str(message.timestamp),
        ("Server: " + message.server.name + ", " if message.server is not None else ""),
        (message.channel.name if message.channel.name is not None else "(No channel name)"),
        message.author.name,
        # incase an int is given (doc says str or int)
        str(message.author.discriminator),
        message.author.id,
        msg)

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.author, 'Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr) 

@bot.event
async def on_ready():
    print("discord.py version: {}".format(discord.__version__))
    print('Running script as: {}#{}({})'.format(bot.user.name, bot.user.discriminator, bot.user.id))
    print('------------------------------------------------------------------')
    if not hasattr(bot, 'game_name'):
        bot.game_name = None
    if not hasattr(bot, 'status'):
        bot.status = discord.Status.online
        await bot.change_presence(status=bot.status)
    # reset these to empty list
    bot.log_servers = []
    bot.log_private_channels_list = []
    if bot.log_all_messages_on_start:
        print("Beginning to dump previous messages to log...")
        log.info("====================== Dumping Previous Messages ======================")
        # first log all servers and channels in servers
        for server in bot.servers:
            for channel in server.channels:
                permissions = channel.permissions_for(server.get_member(bot.user.id))
                if all(getattr(permissions, perm, None) == True for perm in ["read_messages", "read_message_history"]):
                    async for message in bot.logs_from(channel, limit=bot.message_channel_max):
                        log_message(message)
        # now the same for PrivateChannels
        for channel in bot.private_channels:
            async for message in bot.logs_from(channel, limit=bot.message_channel_max):
                log_message(message)
        log.info("====================== End Previous Message Dump ======================")
        print("Finished dumping previous messages!")

def get_status_color():
    if bot.status is None:
        return 0x000000
    elif bot.status == discord.Status.online:
        return 0x43B581
    elif bot.status == discord.Status.idle:
        return 0xFAA61A
    elif bot.status == discord.Status.invisible or bot.status == discord.Status.offline:
        return 0x747F8D
    elif bot.status == discord.Status.dnd or bot.status == discord.Status.do_not_disturb:
        return 0xF04747
    else:
        return 0x000000

@bot.command(pass_context=True)
async def setgame(ctx, game_name : str = None):
    """Sets/Clears users game"""
    if game_name is None:
        print("Erasing game status")
        bot.game_name = None
    else:
        print("Setting game status to \""+game_name+"\"")
        bot.game_name = game_name

    await bot.change_presence(game=discord.Game(name=bot.game_name))
    await bot.say(embed=discord.Embed(title="Game Status", type="rich", timestamp=datetime.utcnow(), colour=0x00FF00, description="Setting game to \"{}\"".format(bot.game_name)))

@bot.command(pass_context=True)
async def setstatus(ctx, status : str = None):
    """Sets status to passed in status; defaults to 'online'"""
    if status is None:
        bot.status = discord.Status.online
    elif status == "online":
        bot.status = discord.Status.online
    elif status == "idle":
        bot.status = discord.Status.idle
    elif status == "offline" or status == "invisible":
        bot.status = discord.Status.invisible
    elif status == "do_not_disturb" or status == "dnd" or status == "do not disturb":
        bot.status = discord.Status.dnd
    else:
        print("Unknown status named \"{}\"\nStatus change cancelled.".format(status))
        await bot.say(embed=discord.Embed(title="Status", type="rich", timestamp=datetime.utcnow(), colour=0xFF0000, description="Unknown status \"{}\"\nStatus change cancelled.".format(status)))
        return

    print("Setting status to \"{}\"".format(bot.status))
    await bot.say(embed=discord.Embed(title="Status", type="rich", timestamp=datetime.utcnow(), colour=get_status_color(), description="Current status set to {}".format(bot.status)))
    await bot.change_presence(game=discord.Game(name=bot.game_name), status=bot.status)

@bot.command(pass_context=True)
async def getstatus(ctx):
    """Returns current user status"""
    await bot.say(embed=discord.Embed(title="Status", type="rich", timestamp=datetime.utcnow(), colour=get_status_color(), description="Status: {}".format(bot.status)))

@bot.command(pass_context=True)
async def getgame(ctx):
    """Returns current user 'game'"""
    await bot.say(embed=discord.Embed(title="Game Status", type="rich", timestamp=datetime.utcnow(), colour=0x00FF00, description="Current Game: {}".format(bot.game_name)))

@bot.command(pass_context=True)
async def killbot(ctx):
    """Kills the selfbot"""
    print("Shutting down selfbot")
    await bot.say(embed=discord.Embed(title="Bot Status", type="rich", timestamp=datetime.utcnow(), colour=0x747F8D, description="Shutting down bot..."))
    await bot.close()
    
@bot.event
async def on_message(message):
    # if author is bot, return
    if message.author.bot:
        return
    # log here
    if bot.log_all_messages or (message.server is not None and message.server.id in bot.log_servers):
        log_message(message)
    elif bot.log_private_channels or message.channel.id in bot.log_private_channels_list:
        log_message(message)
    # check to see if user wants to run a command
    await bot.process_commands(message)
    
@bot.event
async def on_server_join(server):
    if bot.log_on_server_join:
        bot.log_servers.append(server.id)
        
@bot.event
async def on_server_remove(server):
    if server.id in bot.log_servers:
        bot.log_servers.remove(server.id)
        
@bot.event
async def on_channel_create(channel):
    if channel.is_private:
        if bot.log_new_private_channels:
            bot.log_private_channels_list.append(channel.id)
            
@bot.event
async def on_channel_delete(channel):
    if channel.is_private:
        if channel.id in bot.log_private_channels_list:
            bot.log_private_channels_list.remove(channel.id)
        
@bot.command(pass_context=True)
async def logserver(ctx, server_id):
    isLogged = False
    server_name = None
    for server in bot.servers:
        if server_id == server.id:
            server_name = server.name
            if server_id not in bot.log_servers:
                bot.log_servers.append(server_id)
            else:
                await bot.say(embed=discord.Embed(title="Warning", type="rich", timestamp=datetime.utcnow(), colour=0xFFFF00, description=server_name+" is already being logged!"))
                return
            isLogged = True
            break
    if isLogged:
        await bot.say(embed=discord.Embed(title="Success", type="rich", timestamp=datetime.utcnow(), colour=0x00FF00, description=server_name+" is now being logged."))
    else:
        await bot.say(embed=discord.Embed(title="Error", type="rich", timestamp=datetime.utcnow(), colour=0xFF0000, description="'"+str(server_id)+"' is either not a server id, or you are not in the server!"))

@bot.command(pass_context=True)
async def getmessagesfrom(ctx, server_id):
    isLogged = False
    server_name = None
    for server in bot.servers:
        if server.id == server_id:
            server_name = server.name
            # we have the server we want; log past messages from ALL channels we have read perms for
            print("Logging previous messages for "+ server.name +"...")
            log.info("====================== Dumping Previous Messages for "+ server.name +" ======================")
            for channel in server.channels:
                permissions = channel.permissions_for(server.get_member(bot.user.id))
                if all(getattr(permissions, perm, None) == True for perm in ["read_messages", "read_message_history"]):
                    async for message in bot.logs_from(channel, limit=bot.message_channel_max):
                        log_message(message)
            log.info("====================== End Previous Message Dump for "+ server.name +" ======================")
            print("Finished logging previous messages for "+ server.name +".")
            isLogged = True
            break
    if isLogged:
        await bot.say(embed=discord.Embed(title="Success", type="rich", timestamp=datetime.utcnow(), colour=0x00FF00, description=server_name+" was logged successfully!"))
    else:
        await bot.say(embed=discord.Embed(title="Error", type="rich", timestamp=datetime.utcnow(), colour=0xFF0000, description="'"+str(server_id)+"' is either not a server id, or you are not in the server!"))
    
def cleanup_handlers():
    # Clean up log handles
    handles = log.handlers[:]
    for handle in handles:
        handle.close()
        log.removeHandler(handle)

def get_settings():
    if not os.path.isfile('settings.json'):
        # file doesn't exist, create one!
        f = open('settings.json', 'w')
        f.write(json.dumps({"token":"", "log_all_messages_on_start": False, "log_all_messages": False, "log_on_server_join": False, "log_private_channels": False, "log_new_private_channels": False, "ignore_bot_chat": True, "ignore_own_messages": True, "message_global_max": 100000, "message_channel_max": 5000}, indent=4))
        f.close()
        f = None
    # this should ALWAYS execute
    with open('settings.json') as f:
        return json.load(f)

def parse_commandline(argv):
    # get token from command line, if less than 1 (script), print error and exit
    if len(argv) > 1:
        # try to parse args
        try:
            # apparently needs to be sys.argv[1:], or it wont work...
            opts, args = getopt.getopt(argv[1:],"h",["token=", "help"])
        # if no args, print error, usage and exit
        except:
            cleanup_handlers()
            invalid_token()
            usage(argv[0])
            sys.exit(-1)

        for opt, arg in opts:
            # print usage statement and exit
            if opt in ('-h', "--help"):
                cleanup_handlers()
                usage(argv[0])
                sys.exit(0)
            # grab token from arg for discord.py usage
            elif opt == '--token':
                token = arg

        token = token.strip()
        if token is None or token == "":
            cleanup_handlers()
            invalid_token()
            usage(argv[0])
            sys.exit(-1)
    else:
        # DERP! forgot to add this here >.<
        cleanup_handlers()
        invalid_token()
        usage(argv[0])
        sys.exit(-1)

if __name__ == '__main__':
    # attempt to get settings from settings.json (or create file if it doesn't exist)
    settings = get_settings()
    # User token; can be passed in via commandline instead
    token = settings.get('token', None)
    # Do we log all previous messages from all servers & private channels?
    bot.log_all_messages_on_start = settings.get('log_all_messages_on_start', False)
    # Do we log all messages? (This takes precedence over log_on_server_join, log_private_channels and log_new_private_channels)
    bot.log_all_messages = settings.get('log_all_messages', False)
    # Do we log messages when we join a discord server?
    bot.log_on_server_join = settings.get('log_on_server_join', False)
    # Do we log private channels? This takes precedence over log_new_private_channels
    bot.log_private_channels = settings.get('log_private_channels', False)
    # Do we log newly created private channels?
    bot.log_new_private_channels = settings.get('log_new_private_channels', False)
    # Do we ignore bot responses?
    bot.ignore_bot_chat = settings.get('ignore_bot_chat', True)
    # Do we ignore our own messages?
    bot.ignore_own_messages = settings.get('ignore_own_messages', True)
    # this states how many messages we want to cache globally; change to your liking in settings.json
    bot.message_global_max = settings.get('message_global_max', 100000)
    # this states how many previous messages to log per channel; change to your liking in settings.json
    bot.message_channel_max = settings.get('message_channel_max', 5000)
    # set these to nothing
    bot.log_servers = []
    bot.log_private_channels_list = []
    # if no valid token, parse the commandline
    if token is None or token == "":
        # this should exit on fail
        parse_commandline(sys.argv)

    # since this is a self bot, bot=False (don't login)
    # not sure how many messages we need to store, setting to 100k (if that's even possible)
    bot.run(token, bot=False, max_messages=bot.message_global_max)
    # once bot is done running, cleanup handlers
    cleanup_handlers()