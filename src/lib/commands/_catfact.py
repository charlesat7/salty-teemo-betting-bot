import requests
import json

def _catfact(username='chuby1tubby'):
	url = 'https://catfact.ninja/facts'

	params = dict(
		language='en'
	)

	data = requests.get(url=url, params=params)
	binary = data.content
	result = json.loads(binary)

	fact = result['data'][0]['fact']

	return '@' + username + ' did you know: ' + fact 