from selenium import webdriver
import os
from dotenv import load_dotenv
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re
from .driver import ChromeDriverInitializer
from . import custom_exceptions


class GmailHandler(ChromeDriverInitializer):
	
	def __init__(self):
		super().__init__()
		self.__gmail_login_url = 'https://accounts.google.com/v3/signin/identifier?dsh=S-771286175%3A1678191068165506&continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&rip=1&sacu=1&service=mail&flowName=GlifWebSignIn&flowEntry=ServiceLogin&ifkv=AWnogHdAmMwWaukC-7DoZGo7hMp2KM05LkpOfWxLqV7UnpijrqhjNuwhkWU5zzJqXF2AvXjkIiln'

	def get_code_eb(self):

		try:
			self.driver.get(url=self.__gmail_login_url)
			gmail_login_input = self.driver.find_element(by=By.ID, value='identifierId')
			gmail_login_input.send_keys(os.getenv('GMAIL_LOGIN'))
			
			gmail_login_next = self.driver.find_element(by=By.XPATH, value='//*[@id="identifierNext"]/div')
			gmail_login_next.click()
			
			time.sleep(5)
			
			retry = 5
			while retry >= 0:
				try:
					gmail_password_input = self.driver.find_element(by=By.XPATH, value='//*[@id="password"]/div[1]/div/div[1]/input')
					gmail_password_input.send_keys(os.getenv('GMAIL_PASSWORD'))
					break
				
				except Exception as x:
					retry -= 1
					time.sleep(5)
	
			gmail_passw_next = self.driver.find_element(by=By.XPATH, value='//*[@id="passwordNext"]/div/button/span')
			gmail_passw_next.click()
			
			time.sleep(5)
			
			messages_table = self.driver.find_elements(by=By.TAG_NAME, value='table')
			message = messages_table[-1].find_element(by=By.TAG_NAME, value='tr')
			message.click()
			
			time.sleep(5)
			
			messages_divs = self.driver.find_elements(by=By.CSS_SELECTOR, value='div.a3s')
			raw_code_text = messages_divs[-2].get_attribute('innerHTML')
			code = re.findall(r"(?<!\d)\d{4}(?!\d)", raw_code_text)[0]
			print(code)
			
			return code
			
		except Exception as x:
			print(x)
			raise custom_exceptions.UnableToProceedNeedHumanAttention
		
		finally:
			self.driver.close()


# if __name__ == '__main__':
# 	gmail()
