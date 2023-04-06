from selenium import webdriver
import os
from dotenv import load_dotenv
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from .gmail import GmailHandler
from .driver import ChromeDriverInitializer
from selenium.common import exceptions
from . import custom_exceptions

load_dotenv('../.env')


class BankHandlerBase(ChromeDriverInitializer):
	def __init__(self):
		super().__init__()


class BelinvestBankHandler(BankHandlerBase):
	def __init__(self):
		super().__init__()
		self.eb_login_url = 'https://ibank.belinvestbank.by/signin'

	def login(self):
		try:
			self.driver.get(url=self.eb_login_url)
			
			login_button = self.driver.find_element(by=By.ID, value='signinButton')
			login_button.click()
			
			login_input = self.driver.find_element(by=By.ID, value='login_id')
			login_input.clear()
			login_input.send_keys(os.getenv('B_LOGIN'))
			
			password_input = self.driver.find_element(by=By.ID, value='pass')
			password_input.clear()
			password_input.send_keys(os.getenv('B_PASSWORD'))
			
			email_radiobutton = self.driver.find_element(by=By.XPATH,
			                                        value='//*[@id="signin"]/div[2]/div[2]/div[4]/div[1]/div/label[2]')
			email_radiobutton.click()
			
			signin_button = self.driver.find_element(by=By.CLASS_NAME, value='auth-submit')
			signin_button.click()
			try:
				self.driver.find_element(by=By.ID, value='confirmation_close_session')
				close_previous_session_button = self.driver.find_element(by=By.XPATH,
					                                                    value='//*[@id="confirmation_close_session"]/div[3]/a[2]')
				close_previous_session_button.click()
			
			except exceptions.NoSuchElementException or exceptions.ElementNotInteractableException as x:
				print(x)
			
			gmail = GmailHandler()
			code = gmail.get_code_eb()
			
			time.sleep(5)
			
			code_input = self.driver.find_element(by=By.ID, value='key')
			code_input.send_keys(code)
			
			code_submit_button = self.driver.find_element(by=By.XPATH, value='/html/body/main/form/div/div/div[2]/div[3]/div[2]/input')
			code_submit_button.click()
			
			return True
			
		except Exception as x:
			raise custom_exceptions.UnableToProceedNeedHumanAttention
	
	def pay(self):
		try:
			payments_href = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/main/div[1]/div[4]/span/a')
			payments_href.click()
			
			self.driver.find_element(by=By.LINK_TEXT, value='Банковские, финансовые услуги').click()
			
			self.driver.find_element(by=By.LINK_TEXT, value='Банки, НКФО').click()
			
			self.driver.find_element(by=By.LINK_TEXT, value='БТА Банк').click()
			
			self.driver.find_element(by=By.LINK_TEXT, value='Пополнение счета').click()
			
		except Exception as x:
			raise custom_exceptions.UnableToProceedNeedHumanAttention
			