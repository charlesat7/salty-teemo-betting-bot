import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from subprocess import Popen, PIPE
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException



####################
# Global Constants #
####################


GAME_INFO_URL = "https://gameinfo.saltyteemo.com"
CHAMPIONS = {
	1: 'Annie',
	2: 'Olaf',
	3: 'Galio',
	4: 'Twisted Fate',
	5: 'Xin\'Zhao',
	6: 'Ugot',
	7: 'LeBlanc',
	8: 'Vladimir',
	9: 'Fiddlesticks',
	10: 'Kayle',
	11: 'Master Yi',
	12: 'Alistar',
	13: 'Ryze',
	14: 'Sion',
	15: 'Sivir',
	16: 'Soraka',
	17: 'Teemo',
	18: 'Tristana',
	19: 'Warwick',
	20: 'Nunu & Willump',
	21: 'Miss Fortune',
	22: 'Ashe',
	23: 'Tryndamere',
	24: 'Jax',
	25: 'Morgana',
	26: 'Zilean',
	27: 'Singed',
	28: 'Evelynn',
	29: 'Twitch',
	30: 'Karthus',
	31: 'Cho\'Gath',
	32: 'Amumu',
	33: 'Rammus',
	34: 'Anivia',
	35: 'Shaco',
	36: 'Dr. Mundo',
	37: 'Sona',
	38: 'Kassadin',
	39: 'Irelia',
	40: 'Janna',
	41: 'Gangplank',
	42: 'Corki',
	43: 'Karma',
	44: 'Taric',
	45: 'Veigar',
	48: 'Trundle',
	50: 'Swain',
	51: 'Caitlyn',
	53: 'Blitzcrank',
	54: 'Malphite',
	55: 'Katarina',
	56: 'Nocturne',
	57: 'Maokai',
	58: 'Renekton',
	59: 'Jarvan IV',
	60: 'Elise',
	61: 'Orianna',
	62: 'Wukong',
	63: 'Brand',
	64: 'Lee Sin',
	67: 'Vayne',
	68: 'Rumble',
	69: 'Cassiopeia',
	72: 'Skarner',
	74: 'Heimerdinger',
	75: 'Nasus',
	76: 'Nidalee',
	77: 'Udyr',
	78: 'Poppy',
	79: 'Gragas',
	80: 'Pantheon',
	81: 'Ezreal',
	82: 'Mordekaiser',
	83: 'Yorick',
	84: 'Akali',
	85: 'Kennen',
	86: 'Garen',
	89: 'Leona',
	90: 'Malzahar',
	91: 'Talon',
	92: 'Riven',
	96: 'Kog\'Maw',
	98: 'Shen',
	99: 'Lux',
	101: 'Xerath',
	102: 'Shyvana',
	103: 'Ahri',
	104: 'Graves',
	105: 'Fizz',
	106: 'Volibear',
	107: 'Rengar',
	110: 'Varus',
	111: 'Nautilus',
	112: 'Viktor',
	113: 'Sejuani',
	114: 'Fiora',
	115: 'Ziggs',
	117: 'Lulu',
	119: 'Draven',
	120: 'Hecarim',
	121: 'Kha\'Zix',
	122: 'Darius',
	126: 'Jayce',
	127: 'Lissandra',
	131: 'Diana',
	133: 'Quinn',
	134: 'Syndra',
	136: 'Aurelion Sol',
	141: 'Kayne',
	142: 'Zoe',
	143: 'Zyra',
	145: 'Kai\'Sa',
	150: 'Gnar',
	154: 'Zac',
	157: 'Yasuo',
	161: 'Vel\'Koz',
	163: 'Taliyah',
	164: 'Camille',
	201: 'Braum',
	202: 'Jhin',
	203: 'Kindred',
	222: 'Jinx',
	223: 'Tahm Kench',
	236: 'Lucian',
	238: 'Zed',
	240: 'Kled',
	245: 'Ekko',
	254: 'Vi',
	266: 'Aatrox',
	267: 'Nami', #?
	268: 'Azir',
	412: 'Thresh',
	420: 'Illaoi',
	421: 'Rek\'Sai',
	427: 'Ivern',
	429: 'Kalista',
	432: 'Bard',
	497: 'Rakan',
	498: 'Xayah',
	516: 'Ornn',
	518: 'Neeko',
	555: 'Pyke'
}



#####################
# Global Properties #
#####################


# Chromedriver setup
options = Options()
options.headless = True
browser = webdriver.Chrome(chrome_options=options)

# General variables
prev_url = ""
curr_url = ""
first_iteration = True



#############
# Functions #
#############


def fetchHtml(url, delay):
	''' Fetch HTML Function
	
	Uses Selenium to grab the HTML contents of a web page,
	then passes the HTML, as BeautifulSoup, to `parseHtml()`.

	:param url: 	The url of the web page to grab HTML from.
	:param delay: 	The amount of seconds to wait for the page contents to finish loading.
	'''

	browser.get(url)

	time.sleep(0.5)
	if (browser.current_url == "https://ezre.al/error/GAME_NOT_FOUND"):
		print('Yo, there isn\'t a game playing right now.')
		return

	html = ""

	try:
		# Search for an element.
		element_present = EC.presence_of_element_located((By.TAG_NAME, 'b'))
		WebDriverWait(browser, delay).until(element_present)

		# Return page HTMl.
		html = browser.page_source
	except TimeoutException:
		print("Loading timed out.")

	browser.quit()

	if (html):
		soup = BeautifulSoup(html, 'html.parser')
		parseHtml(soup)
	else:
		print('No game info found.')

def parseHtml(soup):
	''' Parse HTML Function

	Uses BeautifulSoup to make an array of all `tr` elements on the page,
	then calculates the average win-rate of both the Blue and Red teams.

	:param soup: 	The BeautifulSoup object passed in from a successful HTML retrieval in `fetchHtml()`.
	'''

	rows = soup.find_all(['tr'])

	blue_total = 0.0
	red_total = 0.0
	blue_count = 0.0
	red_count = 0.0

	for i, row in enumerate(rows):
		if i == 0:
			continue
		elif i == 1:
			print('Blue Champions:')
		elif i == 6:
			print('\nRed Champions:')

		champion_img_uri = row.find('img', class_='champion')['src']
		champion_number = int(champion_img_uri.split('champion/')[1].split('.')[0])
		champion_name = ''

		try:
			champion_name = CHAMPIONS[champion_number]
		except:
			champion_name = 'Unknown'
			pass
		print(champion_name)

		percentages = row.find_all(['b'])

		player_total = 0.0
		player_count = 0.0
		player_average = 0.0

		# Calculate player total.
		for percentage in percentages:
			num = float(percentage.text.split('%')[0])
			if num:
				player_total += num
				player_count += 1.0

		# Calculate player average.
		if player_count:
			player_average = player_total / player_count

		# Update team totals.
		if player_average:
			if i <= 5:
				blue_total += player_average
				blue_count += 1.0
			else:
				red_total += player_average
				red_count += 1.0

	# Calculate team averages.
	if not blue_count:
		blue_count = 1
	if not red_count:
		red_count = 1
	blue_average = round(blue_total / blue_count, 2)
	red_average = round(red_total / red_count, 2)

	print('\nAverage Win Rates:')
	print("Blue Average: {}%".format(blue_average))
	print("Red Average: {}%".format(red_average))



########
# Main #
########


fetchHtml(GAME_INFO_URL, 10)