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
	267: 'Nami',
	268: 'Azir',
	350: 'Yuumi',
	412: 'Thresh',
	420: 'Illaoi',
	421: 'Rek\'Sai',
	427: 'Ivern',
	429: 'Kalista',
	432: 'Bard',
	497: 'Rakan',
	498: 'Xayah',
	516: 'Ornn',
	517: 'Sylas',
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



#############
# Functions #
#############


def fetchHtml(url, delay):
	browser.get(url)
	time.sleep(0.5)

	if 'GAME_NOT_FOUND' in browser.current_url:
		return

	html = ''
	try:
		# Search for any 'b' elements and return False if none found.
		element_present = EC.presence_of_element_located((By.TAG_NAME, 'b'))

		# Wait until element_present is True.
		WebDriverWait(browser, delay).until(element_present)

		html = browser.page_source
	except Exception as e:
		pass

	browser.quit()
	browser.close()

	return html

def getChampionNames():
	soup = None
	champion_names = []
	html = fetchHtml(GAME_INFO_URL, 10)

	if not html:
		print("No HTML")
		return ['lol nope']

	soup = BeautifulSoup(html, 'html.parser')

	table_rows = soup.find_all(['tr'])

	for i, row in enumerate(table_rows):
		if i == 0: 
			continue

		champion_img_uri = row.find('img', class_='champion')['src']
		champion_number = int(champion_img_uri.split('champion/')[1].split('.')[0])
		
		champion_name = ''
		try:
			champion_name = CHAMPIONS[champion_number]
		except:
			champion_name = 'Unknown'

		champion_names.append(champion_name)

	return champion_names