import os
import time
import math
import random
import lib.irc as irc_
from datetime import datetime
from subprocess import Popen, PIPE
from lib.functions_general import *
import lib.functions_commands as commands

class Main:
	def __init__(self, config):
		self.config = config
		self.irc = irc_.irc(config)
		self.socket = self.irc.get_irc_socket_object()

	def run(self):
		irc = self.irc
		sock = self.socket
		config = self.config

		# Initialize reusable properties.
		totals = {'blue_amt': 0, 'blue_bets': 0, 'red_amt': 0, 'red_bets': 0}
		timers = {'!collect': time.time(), 'first_bet': time.time()}
		higher = lower = {}
		bet_complete = False
		betting_started = False

		if config['log_statistics']:
			f = open(config['statistics_file'], 'a+')

		prev_time_int = 0

		while True:
			time_since_collect = int(time.time() - timers['!collect'])
			time_since_first_bet = int(time.time() - timers['first_bet'])

			# Check if 60 minutes has passed yet.
			if time_since_collect > 3600:
				irc.send_message(channel, '!collect')
				timers['!collect'] = time.time()

			# Wait until 170 seconds has passed to bet.
			if time_since_first_bet >= 170 and betting_started and not bet_complete:
				# Check which team is in the lead.
				blue = {'name': 'blue', 'amt': totals['blue_amt'], 'bets': totals['blue_bets']}
				red = {'name': 'red', 'amt': totals['red_amt'], 'bets': totals['red_bets']}
				if (red['amt'] > blue['amt']):
					higher = red
					lower = blue
				else:
					higher = blue
					lower = red

				# Quick mafs.
				x = lower['amt']
				print x
				if x > 0:
					y = 2000 * math.log10(x + 20000) - 8300		# Min 400;		Max ~3,000
					print 'log10 okay: x=%s, y=%s' % (x, y)
				else:
					y = random.randint(500, 1500)
					print 'Using random int: x=%s, y=%s' % (x, y)

				# Bet on the underdog.
				underdog = lower['name']
				bet = int(y)

				# Send the message and record the bet.
				irc.send_message(channel, '!%s %s' % (underdog, bet))
				print 'Bet complete: !%s %s\n' % (underdog, bet)
				bet_complete = True
				betting_started = False

			data = sock.recv(2048).rstrip()

			# Check if the script is still connected to IRC.
			if len(data) == 0:
				pp('Connection was lost, reconnecting...')
				sock = self.irc.get_irc_socket_object()

			# Check for PING; reply with PONG.
			irc.check_for_ping(data)

			# Check if most recent data is a message from Twitch chat.
			if irc.check_for_message(data):
				message_dict = irc.get_message(data)
				channel = message_dict['channel']
				message = message_dict['message']
				username = message_dict['username']


				#######################################
				# Handle messages sent by other users #
				#######################################
				if username != config['username']:
					# Message was sent by @xxsaltbotxx.
					if username == 'xxsaltbotxx':
						# Message contains 'bet complete for'.
						if 'Bet complete' in message:
							# This is the first bet of the game.
							if (totals['blue_amt'] == 0 and totals['red_amt'] == 0):
								timers['first_bet'] = time.time()
								time_since_first_bet = 0
								betting_started = True

								# Set focus to the Twitch tab in Chrome.
								apple_script = '''
									tell application "Google Chrome"
										activate
										set active tab index of first window to 2
									end tell
								'''
								p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
								stdout, stderr = p.communicate(apple_script)

							# Parse values from xxsaltbotxx's message.
							split = message.split(' - Bet complete for ')[1].split(', ')
							team = split[0].lower()				# Team name.
							amt = int(split[1].split('.')[0])	# Bet amount.

							# Increment totals each time a user bets.
							if (team == 'blue'):
								totals['blue_amt'] += amt
								totals['blue_bets'] += 1
							else:
								totals['red_amt'] += amt
								totals['red_bets'] += 1

							print 'Time since first bet: %s s' % time_since_first_bet
							print 'Blue: \t%s shrooms, %s bets' % ("{:,}".format(totals['blue_amt']), totals['blue_bets'])
							print 'Red: \t%s shrooms, %s bets\n' % ("{:,}".format(totals['red_amt']), totals['red_bets'])

						# Message contains 'Betting has ended' or over 3 minutes has passed.
						if 'Betting has ended' in message or time_since_first_bet >= 210:
							if totals['blue_amt'] != 0 and totals['red_amt'] != 0:
								if 'name' not in lower:
									lower['name'] = 'UNKNOWN'

								# Log data to a text file.
								d = datetime.now().strftime('%Y-%m-%d')
								t = datetime.now().strftime('%I:%M%p')
								new_row = '\n%s\t| %s\t| %s  \t\t| %s \t\t| %s  \t\t| %s \t\t| %s     \t\t| %s \t\t| ' % (d, t, totals['blue_amt'], totals['blue_bets'], totals['red_amt'], totals['red_bets'], bet, lower['name'])
								f.write(new_row)
								f.flush()

								# Set all globals back to zero.
								totals = {'blue_amt': 0, 'blue_bets': 0, 'red_amt': 0, 'red_bets': 0}
								timers['first_bet'] = 0
								time_since_first_bet = 0
								bet_complete = False
								betting_started = False

								print 'Betting has ended\n'


				########################################
				# Handle messages sent by your account #
				########################################

				if username == config['username']:
					if config['log_messages']:
						ppi(channel, message, username)

					# Check if the message is a command (i.e. starts with "!{command}").
					if commands.is_valid_command(message) or commands.is_valid_command(message.split(' ')[0]):
						command = message

						# Command is a function (i.e. command should execute a script in the /src/lib/commands/ directory).
						if commands.check_returns_function(command.split(' ')[0]):
							if commands.check_has_correct_args(command, command.split(' ')[0]):
								args = command.split(' ')
								del args[0]
								command = command.split(' ')[0]

								if commands.is_on_cooldown(command, channel):
									pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (command, username, commands.get_cooldown_remaining(command, channel)), channel)
								else:
									# Command (function) is not on cooldown, so send a message to Twitch chat.
									pbot('(%s) (%s)' % (command, username), channel)
									result = commands.pass_to_function(command, args)

									if result:
										# Function returned a valid result.
										pbot(result, channel)
										irc.send_message(channel, result)
										commands.update_last_used(command, channel)

						# Command is not a function and has no arguments (i.e. a simple command with a simple response, such as "!test").
						else:
							if commands.is_on_cooldown(command, channel):
								pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (command, username, commands.get_cooldown_remaining(command, channel)), channel)
							elif commands.check_has_return(command):
								# Command is not on cooldown, so send a message to Twitch chat.
								pbot('(%s) (%s)' % (command, username), channel)
								res = commands.get_return(command)
								pbot(res, channel)
								irc.send_message(channel, res)
								commands.update_last_used(command, channel)
