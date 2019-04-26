import random

def _rand(args):
    min = int(args[0])
    max = int(args[1])

    try:
        return '%s' % random.randint(min, max)
    except ValueError:
        return '!random <min> <max> (use full integers)'
    except:
        return '!random <min> <max>'