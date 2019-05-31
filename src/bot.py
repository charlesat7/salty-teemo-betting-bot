import random
import src.lib.irc as irc_
from datetime import datetime
from subprocess import Popen, PIPE
import src.lib.gameinfo as gameinfo
from src.lib.functions_general import *
import src.lib.functions_commands as commands


class Main:
	def __init__(self, config):
		self.config = config
		self.irc = irc_.irc(config)
		self.socket = self.irc.get_irc_socket_object()

	def run(self):
		global f, higher, lower, time_since_first_bet, blue, red, my_bet

		irc = self.irc
		sock = self.socket
		config = self.config

		# Initialize reusable properties.
		totals = {'blue_amt': 0, 'blue_bets': 0, 'red_amt': 0, 'red_bets': 0}
		timers = {'!collect': time.time(), 'first_bet': time.time()}
		verbal_alert = True
		bet_complete = False
		betting_started = False
		my_balance = 0
		my_last_balance = 0

		if config['log_statistics']:
			f = open(config['statistics_file'], 'a+')

		while True:
			time_since_collect = int(time.time() - timers['!collect'])
			time_since_first_bet = int(time.time() - timers['first_bet'])

			# Check if 60 minutes has passed yet.
			if time_since_collect > 3600:
				irc.send_message(channel, '!collect')
				timers['!collect'] = time.time()

			data = sock.recv(2048).rstrip()

			# Check if the script is still connected to IRC.
			if len(data) == 0:
				pp('Connection was lost, reconnecting...')
				sock = self.irc.get_irc_socket_object()

			# Check for PING; reply with PONG.
			irc.check_for_ping(data)

			# Wait until 170 seconds has passed to bet.
			if time_since_first_bet > 170 and betting_started and not bet_complete:
				# Check which team is in the lead.
				blue = {'name': 'blue', 'amt': totals['blue_amt'], 'bets': totals['blue_bets']}
				red = {'name': 'red', 'amt': totals['red_amt'], 'bets': totals['red_bets']}

				if red['amt'] > blue['amt']:
					higher = red
					lower = blue
				else:
					higher = blue
					lower = red

				my_team = lower['name']

				# Calculate my bet amount.
				my_bet = random.randint(5000, 5005)
				if my_bet > lower['amt']:
					# My bet is needlessly large.
					my_bet = lower['amt']
				elif int(higher['amt'] - lower['amt']) < 5000:
					# My bet would tip the scales.
					my_bet = random.randint(3000, 3005)
					if int(higher['amt'] - lower['amt']) < 1000:
						my_bet = random.randint(1000, 3005)

				# Send the message and record the bet.
				irc.send_message(channel, '!%s %s' % (my_team, my_bet))
				print('--------------------------------')
				print('BET COMPLETE: !%s %s' % (my_team, my_bet))
				print('--------------------------------')
				bet_complete = True
				betting_started = False

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
						# Message contains 'bet complete'.
						if 'Bet complete' in message:
							# This is the first bet of the game.
							if totals['blue_amt'] == 0 and totals['red_amt'] == 0:
								timers['first_bet'] = time.time()
								time_since_first_bet = 0
								betting_started = True

								# Send a message using Messages.app.
								args = [
									'6262099242',
									'%s - A new game has started!' % datetime.now().strftime("%I:%M %p")
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
								if verbal_alert:
									# Popen('say a game is starting'.split())
									Popen('afplay teemo.mp3'.split())

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
							print('Blue: \t%s shrooms, %s bets' % ("{:,}".format(totals['blue_amt']), totals['blue_bets']))
							print('Red: \t%s shrooms, %s bets\n' % ("{:,}".format(totals['red_amt']), totals['red_bets']))

							# The bet was made by myself.
							if 'chuby1tubby' in message.lower():
								bet_complete = True
								betting_started = False
								my_team = team
								my_bet = amt

								# Get the balance from after my bet.
								balance_str = message.split('Your new balance is ')[1].split('.')[0]
								my_balance = int(balance_str) + my_bet
								print('\n----------------------------------------------')
								print('My balance: %s mushrooms (before bet)' % my_balance)
								print('----------------------------------------------')

								# Analyze the balance.
								balance_diff = my_balance - my_last_balance
								if balance_diff > 0 and my_last_balance:
									# Most recent bet was a win (unless I collected 2000+ mushrooms).
									print('----------------------------------')
									print('Previous game was a win! (%s --> %s)' % (my_last_balance, my_balance))
									print('----------------------------------\n')

								my_last_balance = my_balance
						
						# Message contains 'Betting has ended' or over 3 minutes has passed.
						if 'Betting has ended' in message or time_since_first_bet >= 240:
							if totals['blue_amt'] != 0 and totals['red_amt'] != 0:
								# Log data to a text file.
								dt = datetime.now()
								new_row = '\n%s\t| %s  \t\t| %s \t\t| %s  \t\t| %s \t\t| %s \t\t| %s     \t| %s \t\t| ' % (
									dt, totals['blue_amt'], totals['blue_bets'], totals['red_amt'],
									totals['red_bets'], my_balance, my_bet, my_team)
								f.write(new_row)
								f.flush()

								print('Betting has ended')
								print('--------------------')
								print('Your bet: !%s %s' % (my_team, my_bet))

								if my_team == 'blue':
									payout = int(float((float(my_bet) / float(totals['blue_amt']))) * float(totals['red_amt']))
									print('%s / %s * %s = %s' % (my_bet, totals['blue_amt'], totals['red_amt'], payout))
								else:
									payout = int(float((float(my_bet) / float(totals['red_amt']))) * float(totals['blue_amt']))
									print('%s / %s * %s = %s' % (my_bet, totals['red_amt'], totals['blue_amt'], payout))

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

					if '!collect' in message:
						timers['!collect'] = time.time()

					if '!mute' in message:
						verbal_alert = False

					if '!unmute' in message:
						verbal_alert = True

					if '!names' in message:
						names_list = gameinfo.getChampionNames()
						names_str = ', '.join(names_list)
						result = '@Chuby1Tubby I found these champions in the match: ' + names_str
						irc.send_message(channel, result)

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

