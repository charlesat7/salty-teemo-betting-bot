import re
import socket
import sys
from time import sleep
from src.lib.functions_general import *


class irc:

	def __init__(self, config):
		self.config = config
		self.sock = None

	@staticmethod
	def check_for_message(data):
		if re.match(
				r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$',
				data):
			return True

	@staticmethod
	def check_is_command(self, message, valid_commands):
		for command in valid_commands:
			if command == message:
				return True

	@staticmethod
	def check_for_connected(self, data):
		if re.match(r'^:.+ 001 .+ :connected to TMI$', data):
			return True

	@staticmethod
	def check_for_ping(self, data):
		if data[:4] == "PING":
			self.sock.send('PONG')

	@staticmethod
	def get_message(self, data):
		return {
			'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
			'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
			'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0].decode('utf8')
		}

	@staticmethod
	def check_login_status(self, data):
		if re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data):
			return False
		else:
			return True

	@staticmethod
	def send_message(self, channel, message):
		# Loop each send 3 times in case the first one or two fail.
		for i in range(3):
			# Wait 0.5 second, just in case a message was sent a moment ago.
			sleep(0.5)
			self.sock.send(b'PRIVMSG %s :%s\r\n' % (channel, message.encode('utf-8')))

	@property
	def get_irc_socket_object(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(10)

		self.sock = sock

		try:
			sock.connect(('irc.chat.twitch.tv', 6667))
		except:
			sys.exit()

		sock.settimeout(None)

		sock.send('USER %s\r\n' % self.config['username'])
		sock.send('PASS %s\r\n' % self.config['oauth_password'])
		sock.send('NICK %s\r\n' % self.config['username'])

		if self.check_login_status(sock.recv(1024)):
			pass
		else:
			sys.exit()

		self.join_channels(self.channels_to_string(self.config['channels']))

		return sock

	@staticmethod
	def channels_to_string(channel_list):
		return ','.join(channel_list)

	@staticmethod
	def join_channels(self, channels):
		self.sock.send('JOIN %s\r\n' % channels)
		pp('Connection established.')

	@staticmethod
	def leave_channels(self, channels):
		pp('Leaving channels %s,' % channels)
		self.sock.send('PART %s\r\n' % channels)
		pp('Left channels.')
