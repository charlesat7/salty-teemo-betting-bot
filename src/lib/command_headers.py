from src.config.config import *

commands = {
	'!test': {
		'limit': 5,
		'return': '@%s I hear you MrDestructoid' % config['username']
	},
	'!beemo': {
		'limit': 5,
		'return': '@Chuby1Tubby Fact: beemo is the cutest champion in the whole world <3.'
	},
	'!catfact': {
		'limit': 10,
		'argc': 0,
		'return': 'command'
	},
	'!rand': {
		'limit': 10,
		'argc': 2,
		'return': 'command'
	}
}

for channel in config['channels']:
	for command in commands:
		commands[command][channel] = {'last_used': 0}
