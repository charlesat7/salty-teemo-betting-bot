global config

config = {
	# Username must be all lowercase.
	'username': 'mytwitchusername',

	# Get your password from http://twitchapps.com/tmi/.
	'oauth_password': 'oauth:xxxxxxxxxxxxxxxxxxxxxxx',

	# Channel name must start with a "#" followed by an all-lowercase channel name.
	# Example for joining three separate channels --> 'channels': ['#saltyteemo', '#rtgamecrowd', '#kitboga'],
	'channels': ['#saltyteemo'],

	# Display user messages from Twitch Chat.
	'log_messages': True,

	# Log betting statistics from chat to a text file.
	'log_statistics': True,

	# Select where statistics will be saved on the device.
	'statistics_file': 'stats.txt'
}
