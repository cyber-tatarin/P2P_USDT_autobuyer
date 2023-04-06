from abc import ABC, abstractmethod
from seleniumwire.undetected_chromedriver import Chrome, ChromeOptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


class IncognitoDriverInitializer(ABC):
	def __init__(self):
		options = {}
		# chrome_options = Options()
		chrome_options = ChromeOptions()
		chrome_options.add_argument('--disable-blink-features=AutomationControlled')
		chrome_options.add_argument("--incognito")
		# chrome_options.add_argument("--disable-dev-shm-usage")
		# self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
		self.driver = Chrome(seleniumwire_options=options, options=chrome_options)
		self.driver.set_window_size(1280, 1080)
		self.driver.implicitly_wait(40)
		
		
class ChromeDriverInitializer(ABC):
	def __init__(self):
		# options = {}
		chrome_options = Options()
		chrome_options.add_argument('--disable-blink-features=AutomationControlled')
		# chrome_options = ChromeOptions()
		# chrome_options.add_argument('--disable-blink-features=AutomationControlled')
		# chrome_options.add_argument("--incognito")
		# chrome_options.add_argument("--disable-dev-shm-usage")
		self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
		# self.driver = Chrome(seleniumwire_options=options, options=chrome_options)
		self.driver.set_window_size(1280, 1080)
		self.driver.implicitly_wait(40)
		