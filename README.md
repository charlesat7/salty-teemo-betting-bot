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


Betting in Salty Teemo
======================

Betting is handled by the file `bot.py`.
