from src.config.config import *

commands = {
	'!test': {
		'limit': 1,
		'return': 'I hear you, @Chuby1Tubby. MrDestructoid'
	},

	'!PING': {
		'limit': 10,
		'return': 'PONG'
	},

	'!last': {
		'limit': 1,
		'return': '@Chuby1Tubby Your last bet was for RED team. MrDestructoid'
	},

	'!sangokaku': {
		'limit': 1,
		'return': '@Sangokaku is a tree that pretends to be a human in Twitch chat. MiniK rtgameTree'
	}
}


for channel in config['channels']:
	for command in commands:
		commands[command][channel] = {}
		commands[command][channel]['last_used'] = 0
