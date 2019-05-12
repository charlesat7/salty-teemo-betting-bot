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
		my_bet = 0
		my_team = ''
		verbalAlert = True

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

			# Wait until 160 seconds has passed to bet.
			if time_since_first_bet >= 160 and betting_started and not bet_complete:
				# Check which team is in the lead.
				blue = {'name': 'blue', 'amt': totals['blue_amt'], 'bets': totals['blue_bets']}
				red = {'name': 'red', 'amt': totals['red_amt'], 'bets': totals['red_bets']}
				if red['amt'] > blue['amt']:
					higher = red
					lower = blue
				else:
					higher = blue
					lower = red

				x = lower['amt']
				y = x / 20
				if y < 500:
					y = random.randint(500, 800)
				elif y >= 1500:
					y = random.randint(1200, 1500)

				my_bet = int(y)
				my_team = lower['name']

				# Send the message and record the bet.
				irc.send_message(channel, '!%s %s' % (my_team, my_bet))
				print(
					'--------------------------------\nBET COMPLETE: !%s %s\n--------------------------------'
					% (my_team, my_bet))
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
							if totals['blue_amt'] == 0 and totals['red_amt'] == 0:
								timers['first_bet'] = time.time()
								time_since_first_bet = 0
								betting_started = True

								# Set focus to the Twitch tab in Chrome.
								p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
								p.communicate('''
									tell application "Google Chrome"
										activate
										set active tab index of first window to 2
									end tell
								''')

								# Send a message using Messages.app.
								args = [
									'6262099242',
									'{} - A new game has started!'.format(datetime.now().strftime("%I:%M %p"))
								]
								p_message = Popen(
									['osascript', '-'] + args,
									stdin=PIPE,
									stdout=PIPE,
									stderr=PIPE,
									universal_newlines=True
								)
								p_message.communicate('''
									on run {targetBuddyPhone, targetMessage}
										tell application "Messages"
											set targetService to 1st service whose name = "SMS"
											set targetBuddy to buddy targetBuddyPhone of targetService
											send targetMessage to targetBuddy
										end tell
									end run
								''')

								# Verbally notify that a game has started.
								if verbalAlert:
									Popen('say a game is starting'.split())

							# Parse values from xxsaltbotxx's message.
							split = message.split(' - Bet complete for ')[1].split(', ')
							team = split[0].lower()  # Team name.
							amt = int(split[1].split('.')[0])  # Bet amount.

							# Increment totals each time a user bets.
							if team == 'blue':
								totals['blue_amt'] += amt
								totals['blue_bets'] += 1
							else:
								totals['red_amt'] += amt
								totals['red_bets'] += 1

							print('Time since first bet: %s s' % time_since_first_bet)
							print('Blue: \t%s shrooms, %s bets' %
													("{:,}".format(totals['blue_amt']), totals['blue_bets']))
							print('Red: \t%s shrooms, %s bets\n' %
													("{:,}".format(totals['red_amt']), totals['red_bets']))

							# The bet was made by myself.
							if '@Chuby1Tubby' in message:
								bet_complete = True
								betting_started = False
								my_team = team
								my_bet = amt

						# Message contains 'Betting has ended' or over 3 minutes has passed.
						if 'Betting has ended' in message or time_since_first_bet >= 240:
							if totals['blue_amt'] != 0 and totals['red_amt'] != 0:
								# Log data to a text file.
								# d = datetime.now().strftime('%Y-%m-%d')
								# t = datetime.now().strftime('%I:%M%p')
								# new_row = '\n%s\t| %s\t| %s  \t\t| %s \t\t| %s  \t\t| %s \t\t| %s     \t\t| %s \t\t| ' % (
								# 	d, t, totals['blue_amt'], totals['blue_bets'], totals['red_amt'],
								# 	totals['red_bets'], my_bet, my_team)
								# f.write(new_row)
								# f.flush()

								print('Betting has ended')
								print('--------------------')
								print('Your bet: !%s %s' % (my_team, my_bet))

								payout = 0.0
								if my_team == 'blue':
									payout = my_bet / totals['blue_amt'] * totals['red_amt']
								else:
									payout = my_bet / totals['red_amt'] * totals['blue_amt']
								print('Your payout: %s mushrooms' % (payout))

								# Set all globals back to zero.
								totals = {'blue_amt': 0, 'blue_bets': 0, 'red_amt': 0, 'red_bets': 0}
								timers['first_bet'] = 0
								time_since_first_bet = 0
								bet_complete = False
								betting_started = False

				########################################
				# Handle messages sent by your account #
				########################################

				if username == config['username']:
					if config['log_messages']:
						ppi(channel, message, username)

					if '!mute' in message:
						verbalAlert = False
						print('Alerts muted.')
					elif '!unmute' in message:
						verbalAlert = True
						print('Alerts unmuted.')

					if '!skip' in message:
						bet_complete = True
						print('Skipping the current round.')
						irc.send_message(channel, '@chuby1tubby Betting paused until next round.')

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
									pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' %
														(command, username,
															commands.get_cooldown_remaining(command, channel)), channel)
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
								pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' %
													(command, username,
														commands.get_cooldown_remaining(command, channel)), channel)
							elif commands.check_has_return(command):
								# Command is not on cooldown, so send a message to Twitch chat.
								pbot('(%s) (%s)' % (command, username), channel)
								res = commands.get_return(command)
								pbot(res, channel)
								irc.send_message(channel, res)
								commands.update_last_used(command, channel)

