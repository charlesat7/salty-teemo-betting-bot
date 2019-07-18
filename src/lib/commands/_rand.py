import random


def _rand(args):
	_min = int(args[0])
	_max = int(args[1])

	try:
		return '%s' % random.randint(_min, _max)
	except ValueError:
		return '!random <min> <max> (use full integers)'
	except:
		return '!random <min> <max>'
