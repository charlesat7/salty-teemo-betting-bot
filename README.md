Salty Teemo Betting Bot
==========

This is a fork of the twitch-bot made by aidanrwt: https://github.com/aidanrwt/twitch-bot
It is a simple Twitch chat/irc bot written in Python 2.7.16, modified to interact with the Salty Teemo channel.

Getting Started
============
* Ensure your system has Python 2.7 installed: `python --version`
* Install the `requests` package: `pip install requests`
* Clone the Git repository: `git clone https://github.com/knakamura13/salty-teemo-betting-bot`
* Replace all of the placeholders in `config.py` with your own username, oauth token, channels, etc.
* Make the serve.py script executable: `chmod +x /serve.py`
* Run the serve.py script: `./serve.py` or `python serve.py`

Adding your own commands
========================

Custom commands should be added to: `lib/command_headers.py`. 
These are commands that the bot will listen for and respond to accordingly.
There are examples already in `command_headers.py` for you to look at.

#### Simple Commands
The `limit` parameter is the minimum time between uses that you want to allow for that command.
If your command is only going to return a string, such as the `!hello` command, don't include the `argc` parameter. 
Place the string you wish to be returned to the user in the `return` parameter. This is what the bot will type in the Twitch chat for everyone to see.

```python
'!hello': {
	'limit': 10,
	'return': 'Hello from the Python code!'
}
```

#### Complex Commands (functions)
Let's say we want a command which will take two arguments and perform logic based on the arguments. 
The command is `!rand` and it will take a `minimum` and `maximum` argument. We will limit this command to be used once every 10 seconds.

This command is already created for you:

```python
'!rand': {
	'limit': 10,
	'argc': 2,
	'return': 'command'
}
```

And then in `lib/commands/_rand.py`, you will find the following: 

```python
import random

def _rand(args):
	min = int(args[0])
	max = int(args[1])
	
	try:
		return '%s' % random.randint(min, max)
	except ValueError:
		return '!random <min> <max> (use full integers)'
	except:
		return '!random <min> <max>'
```

Now, if a user types `!rand 5 10` into the Twitch chat, the bot will respond with a number between 5 and 10.

Notice that both the filename and the function name are `_rand`. Each command should have a new file named `_commandName.py` with a single function `_commandName(args)`, where `commandName` is the phrase that will trigger the command from Twitch chat, i.e. `!commandName`. The underscores ensure that the function name will not overwrite existing python functions/methods.


Betting in Salty Teemo
======================

The code that determines which team to bet on and how many mushrooms to bet is the following:
```
# bot.py lines 65-67:

# Bet on the underdog.
underdog = lower['name']
bet = int(y)
```
where `y` is calculated beforehand using a basic algorithm. You can replace `int(y)` with any integer to change how much you want to bet.


Reading other peoples' messages
===============================
The relevant code here is the following:
```
# bot.py lines 93-98:

#######################################
# Handle messages sent by other users #
#######################################
if username != config['username']:
	# Message was sent by @xxsaltbotxx.
	if username == 'xxsaltbotxx':
```
where `xxsaltbotxx` is a specific user that is being tracked. 
If you want to print out all messages from someone with the username `twitchuser12`, you can add this code as an additional `if` statement:
```
	if username == 'twitchuser12':
		print('%s says: %s' % (username, mesage))
```
