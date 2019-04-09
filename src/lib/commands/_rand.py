import random

def _rand(args):
  min = int(args[0])
  max = int(args[1])
    
  usage = '!random <min> <max>'
  
  # carry out validation
  try:
    return random.randint(min, max)
  except ValueError:
    return '!random <min> <max> (use full integers)'
  except:
    return usage