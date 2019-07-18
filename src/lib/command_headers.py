from src.config.config import *

commands = {
	# The simplest form of a command that returns a string to chat.
	'!test': {
		'limit': 5,
		'return': '@%s I hear you ' % config['username']
	},
	# An example of a complex command that executes a REST API call.
	'!catfact': {
		'limit': 10,
		'argc': 0,
		'return': 'command'
	},
	# An example of a simple command that takes two arguments.
	'!rand': {
		'limit': 10,
		'argc': 2,
		'return': 'command'
	}
}

for channel in config['channels']:
	for command in commands:
		commands[command][channel] = {'last_used': 0}