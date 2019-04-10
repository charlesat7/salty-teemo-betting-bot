"""
Simple IRC Bot for Twitch.tv

Developed by Aidan Thomson <aidraj0@gmail.com>
"""

import time
import lib.irc as irc_
from lib.functions_general import *
import lib.functions_commands as commands

class Roboraj:

	def __init__(self, config):
		self.config = config
		self.irc = irc_.irc(config)
		self.socket = self.irc.get_irc_socket_object()

	def createCustomResponseForUser(self, channel, username, _username, message, _message, _response, irc):
		if (username == _username and _message in message):
			time.sleep(2)
			irc.send_message(channel, _response)

	def run(self):
		irc = self.irc
		sock = self.socket
		config = self.config

		# Initialize current bet stats per team.
		totals = {}
		totals['blue_amt'] = 0
		totals['blue_bets'] = 0
		totals['red_amt'] = 0
		totals['red_bets'] = 0

		while True:
			data = sock.recv(config['socket_buffer_size']).rstrip()

			if len(data) == 0:
				pp('Connection was lost, reconnecting.')
				sock = self.irc.get_irc_socket_object()

			if config['debug']:
				print data

			# check for ping, reply with pong
			irc.check_for_ping(data)

			if irc.check_for_message(data):
				message_dict = irc.get_message(data)

				channel = message_dict['channel']
				message = message_dict['message']
				username = message_dict['username']


				#######################################
				# Handle messages sent by other users #
				#######################################

				if (username != 'chuby1tubby'):
					# Message was sent by @RyuOz.
					self.createCustomResponseForUser(channel, username, 'ryuoz', message, '!beemo', '@RyuOz reminds you to always bet on beemo. <3', irc)

					# Message was sent by @Sangokaku.
					self.createCustomResponseForUser(channel, username, 'sangokaku', message, '!test', 'Oh hi there @Sangokaku VoHiYo', irc)
					self.createCustomResponseForUser(channel, username, 'sangokaku', message, '!balance', '@Sangokaku Show off DansGame', irc)

					# Message was sent by @xxsaltbotxx.
					if (username == 'xxsaltbotxx'):
						# Message contains 'bet complete for'.
						if ('Bet complete for' in message):
							# Parse values from Salt Bot's message.
							split = message.split(' - Bet complete for ')
							usr = split[0]
							split = split[1].split(', ')
							team = split[0].lower()
							amt = int(split[1].split('.')[0])

							# Copy shellfish's bet.
							if ('you_are_being_shellfish' in message):
								# Use (n)% of shellfish's bet.
								n = 50
								amt = int(amt * n/100)

								# Wait (t) seconds.
								t = 5
								time.sleep(t)

								# Send a message. Ex: !blue 100
								irc.send_message(channel, '!%s %s' % (team, amt))

								# Wait (t) second.
								time.sleep(t)

								# Send a message. Ex: !collect
								irc.send_message(channel, '!collect')

								# Log information to the console.
								print('\n\nSHELLFISH BET (%s) (%s)\n' % (team, amt))
							else:
								# Increment totals each time a user bets.
								if (team == 'blue'):
									totals['blue_amt'] += amt
									totals['blue_bets'] += 1
								else:
									totals['red_amt'] += amt
									totals['red_bets'] += 1

								# Log information to the console.
								print('\nBlue: \t%s mushrooms with %s bets.' % (totals['blue_amt'], totals['blue_bets']))
								print('Red: \t%s mushrooms with %s bets.' % (totals['red_amt'], totals['red_bets']))

						# Message contains 'Betting has ended'.
						if ('Betting has ended' in message):
							if (totals['blue_amt'] != 0 and totals['red_amt'] != 0):
								# Set all totals back to zero.
								totals['blue_amt'] = 0
								totals['blue_bets'] = 0
								totals['red_amt'] = 0
								totals['red_bets'] = 0

								# Log information to the console.
								print('BETTING HAS ENDED')

					# Skip the rest of this loop iteration.
					continue


				##########################################
				# Handle commands sent by my own account #
				##########################################

				ppi(channel, message, username)

				# check if message is a command with no arguments
				if commands.is_valid_command(message) or commands.is_valid_command(message.split(' ')[0]):
					command = message

					if commands.check_returns_function(command.split(' ')[0]):
						if commands.check_has_correct_args(command, command.split(' ')[0]):
							args = command.split(' ')
							del args[0]

							command = command.split(' ')[0]

							if commands.is_on_cooldown(command, channel):
								pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (
									command, username, commands.get_cooldown_remaining(command, channel)), 
									channel
								)
							else:
								pbot('Command is valid an not on cooldown. (%s) (%s)' % (
									command, username), 
									channel
								)
								
								result = commands.pass_to_function(command, args)
								commands.update_last_used(command, channel)

								if result:
									resp = '%s' % (result)
									pbot(resp, channel)

									time.sleep(1)
									irc.send_message(channel, resp)

					else:
						if commands.is_on_cooldown(command, channel):
							pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (
									command, username, commands.get_cooldown_remaining(command, channel)), 
									channel
							)
						elif commands.check_has_return(command):
							pbot('Command is valid and not on cooldown. (%s) (%s)' % (
								command, username), 
								channel
							)
							commands.update_last_used(command, channel)
							resp = '%s' % (commands.get_return(command))
							commands.update_last_used(command, channel)

							pbot(resp, channel)

							time.sleep(1)
							irc.send_message(channel, resp)
