from src.config.config import *

commands = {
	'!test': {
		'limit': 0,
		'return': 'I hear you, @Chuby1Tubby. MrDestructoid'
	},

	'!sango': {
		'limit': 30,
		'return': 'Sango-Kaku, or Coral-Bark Maple, is a type of Japanese maple tree with pinkish-red bark.'
	},

	'!beemo': {
		'limit': 30,
		'return': '/me Teemo reminds you to bee smart with your mushrooms. CosmicBrain'
	}
}


for channel in config['channels']:
	for command in commands:
		commands[command][channel] = {}
		commands[command][channel]['last_used'] = 0
