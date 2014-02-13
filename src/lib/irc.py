import socket, re, time, sys
from functions_general import *
import thread
import time

class irc:
	
	def __init__(self, config):
		self.config = config

	def check_for_message(self, data):
		if re.match(r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$', data):
			return True

	def check_is_command(self, message, valid_commands):
		for command in valid_commands:
			if command == message:
				return True

	def check_for_connected(self, data):
		if re.match(r'^:.+ 001 .+ :connected to TMI$', data):
			return True

	def check_for_ping(self, data):
		if data[:4] == "PING": 
			self.sock.send('PONG')

	def get_message(self, data):
		return {
			'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
			'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
			'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0].decode('utf8')
		}

	def check_login_status(self, data):
		if re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data):
			return False
		else:
			return True

	def send_message(self, channel, message):
		for i in range(3):
			# Wait 0.5 second, just in case a message was sent a moment ago.
			time.sleep(0.5)
			self.sock.send(b'PRIVMSG %s :%s\r\n' % (channel, message.encode('utf-8')))

	def get_irc_socket_object(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(10)

		self.sock = sock

		try:
			sock.connect(('irc.chat.twitch.tv', 6667))
		except:
			pp('Cannot connect to server (%s:%s).' % ('irc.chat.twitch.tv', 6667), 'error')
			sys.exit()

		sock.settimeout(None)

		sock.send('USER %s\r\n' % self.config['username'])
		sock.send('PASS %s\r\n' % self.config['oauth_password'])
		sock.send('NICK %s\r\n' % self.config['username'])

		if self.check_login_status(sock.recv(1024)):
			pass
		else:
			pp('Login unsuccessful. (hint: make sure your oauth token is set in self.config/self.config.py).', 'error')
			sys.exit()

		self.join_channels(self.channels_to_string(self.config['channels']))

		return sock

	def channels_to_string(self, channel_list):
		return ','.join(channel_list)

	def join_channels(self, channels):
		self.sock.send('JOIN %s\r\n' % channels)
		pp('Connection established.')

	def leave_channels(self, channels):
		pp('Leaving chanels %s,' % channels)
		self.sock.send('PART %s\r\n' % channels)
		pp('Left channels.')
