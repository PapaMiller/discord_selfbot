# discord_selfbot
My own selfbot for Discord, using discord.py

## Notes
- Results are always returned as a rich embed, to help differentiate between the user and selfbot output.
- Current command prefix is: "\>".
- On selfbot start, user status is set to "online"
- When using the selfbot, any changes to status or game from the bot will not show up on your end. They do, however, show up to everyone else.

## Command List
- \>setgame | sets Playing to whatever you pass in, or clears it if only \>setgame is called
- \>setstatus | sets users status based on what was passed in. Defaults to "online" if nothing passed in
    - Available options are: online, idle, dnd, do_not_disturb, "do not disturb", invisible, offline
- \>getgame | returns the current game name
- \>getstatus | returns the current user status
- \>getmessagesfrom \<server id\> | get past messages from server id
    - \>getmessagesfrom \<server id\> \<amount\> | get past messages from server id, up to passed in amount (defaults to message_channel_max in settings.json if not passed in)
- \>logserver \<server id\> | set bot to log messages from server id; only useful if log_all_messages is false
- \>setunflip \<true/false\> | sets what the bot does if it sees a "flipped table"; if true, "unflips" table
- \>setunflipself \<true/false\> | sets what the bot does if you "flip" a table; if true, "unflips" your "flipped" table
- \>killbot | shuts down the selfbot
- \>help | returns help stetement for commands
    - \>help \<command\> | return help statement for specific command
    
## Explanation of settings in settings.json file
##### Note: Do NOT copy and paste the settings below with the comments into settings.json as is! (comments are not allowed in json)
```js
{
    "token": "YOUR_TOKEN_HERE", // this is your token
    "log_all_messages_on_start": false, // do you want to get all previous messages from all servers and pms?
    "log_all_messages": false,  // do you want to log any messages while you use the selfbot script?
    "log_on_server_join": false,  // do you want to automatically log messages when you join/create a server?
    "log_private_channels": false,  // do you want to automatically log private channel messages?
    "log_new_private_channels": false,  // do you want to automatically log new private channel messages?
    "ignore_bot_chat": true,  // do you want to ignore messages sent by bots?
    "ignore_own_messages": true,  // do you want to ignore logging your own messages (this includes selfbot messages)?
    "message_global_max": 100000, // see max_messages from https://discordpy.readthedocs.io/en/latest/api.html#discord.Client
                                  // don't change if you aren't sure what this does
    "message_channel_max": 5000 // see limit from https://discordpy.readthedocs.io/en/latest/api.html#discord.Client.logs_from
                                // don't change if you aren't sure what this does
    "unflip_tables": false,     // do we "unflip" "flipped" tables?
    "unflip_own_tables": false  // do we "unflip" our own "flipped" tables?
}
```
    
## How to run
1. Install [discord.py](https://github.com/Rapptz/discord.py#installing)
2. Open up discord and open the inspector window (`CTRL` + `SHIFT` + `I`)
3. Go to the `Application` page
4. Under `Storage`, select `Local Storage`, and then `discordapp.com`
5. Find the `token` row and copy the value that is in quotes
6. run selfbot.py
    - add `token` value to "token" in settings.json, change any settings if desired, and run selfbot.py again
    - example if running with token on command line: `python3 selfbot.py --token=<YOUR_TOKEN_HERE>`
