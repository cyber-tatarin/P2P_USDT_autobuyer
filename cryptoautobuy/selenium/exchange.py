import re
from selenium import webdriver
import os
from dotenv import load_dotenv
import time
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pickle
from .captchabp import get_position
from selenium.common import exceptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from . import custom_exceptions
from abc import ABC, abstractmethod
from .driver import ChromeDriverInitializer, IncognitoDriverInitializer

load_dotenv('../.env')


class ExchangeHandlerBase(ChromeDriverInitializer):
    def __init__(self):
        super().__init__()
        self._login_button_click_counter = 3
        self._wrong_captcha_clicks_counter = 2
        self._code_input_retries = 3
    
    @abstractmethod
    def login_to_exchange(self):
        pass
    
    @staticmethod
    def check_retries_limit(counter, driver):
        if counter < 1:
            driver.close()
            raise custom_exceptions.RetriesLimitExceeded
        counter -= 1
        return counter


class OKXExchangeHandler(ExchangeHandlerBase):
    def __init__(self):
        super().__init__()
        self.exchange_url = 'https://www.okx.com/account/login'
        self.p2p_url = 'https://www.okx.com/p2p-markets/byn/buy-usdt'
        self.code_inputs = None
    
    def close_popup_okx(self):
        try:
            self.driver.find_element(by=By.CSS_SELECTOR, value='button.geetest_refresh').click()
            time.sleep(4)
            self.driver.find_element(by=By.CSS_SELECTOR, value='button.geetest_close').click()
            time.sleep(2)
        except exceptions.ElementNotInteractableException:
            self.driver.refresh()
    
    def login_to_exchange(self):
        try:
            self.driver.get(url=self.exchange_url)
            
            while True:
                while True:
                    try:
                        
                        login_input_exc = self.driver.find_element(by=By.XPATH,
                                                                   value='//*[@id="phone-area-container"]/div/div/input')
                        login_input_exc.send_keys(Keys.CONTROL + "a")
                        login_input_exc.send_keys(Keys.DELETE)
                        login_input_exc.send_keys(int(os.getenv('EXC_LOGIN')))
                        
                        password_input_exc = self.driver.find_element(by=By.XPATH,
                                                                      value='//*[@id="login-password-input"]')
                        password_input_exc.send_keys(Keys.CONTROL + "a")
                        password_input_exc.send_keys(Keys.DELETE)
                        password_input_exc.send_keys(os.getenv('EXC_PASSWORD'))
                        
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="login-submit-btn"]/span'))
                        ).click()
                        print('clicking login button')
                        # driver3.find_element(by=By.XPATH, value='//*[@id="login-submit-btn"]/span').click()
                        
                        time.sleep(5)
                        
                        puzzle_piece = self.driver.find_element(by=By.CSS_SELECTOR, value='div.geetest_slice_bg')
                        puzzle_piece_style = puzzle_piece.get_attribute('style')
                        puzzle_piece_url = re.search(r'https.*g', puzzle_piece_style)[0]
                        
                        full_image = self.driver.find_element(by=By.CSS_SELECTOR, value='div.geetest_bg')
                        full_image_style = full_image.get_attribute('style')
                        full_image_url = re.search(r'https.*g', full_image_style)[0]
                        
                        break
                    
                    except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException):
                        self._login_button_click_counter = self.check_retries_limit(
                            self._login_button_click_counter, self.driver)
                        self.close_popup_okx()
                        self.driver.refresh()
                
                try:
                    print('defining location')
                    puzzle_piece_y = puzzle_piece.location['y']
                    puzzle_piece_x = puzzle_piece.location['x']
                    
                    print(puzzle_piece_y, puzzle_piece_x, '-- y, x')
                    print(full_image_url)
                    print(puzzle_piece_url)
                    
                    hole_x = get_position(full_image_url, puzzle_piece_url, puzzle_piece_y) + 100 + 456
                    # get_position('https://static.geetest.com/captcha_v4/d2ce0cc595/slide/2837248933/2023-01-20T11/bg/01be763d94064ce5a9f180c879f2d3e6.png',
                    #              'https://static.geetest.com/captcha_v4/d2ce0cc595/slide/8e42608485/2023-01-20T11/slice/170e93ca68914c72b98a7c58775ebb17.png')
                    
                    x_offset = hole_x - puzzle_piece_x
                    print(hole_x, puzzle_piece_x, '-- hole, puzzle')
                    print(x_offset, '-- x_offset')
                    time.sleep(1)
                    ActionChains(self.driver).click_and_hold(puzzle_piece).pause(1).move_by_offset(x_offset,
                                                                                                   0).release().perform()
                    print('droped')
                    
                    time.sleep(2)
                    
                    self.code_inputs = self.driver.find_elements(by=By.CSS_SELECTOR, value='input.code-input')
                    print(self.code_inputs)
                    if self.code_inputs:
                        print('break, we go further')
                        break
                    
                    print('no code inputs. reload')
                    raise exceptions.NoSuchElementException
                
                # self.__wrong_captcha_clicks_counter = self.check_retries_limit(self.__wrong_captcha_clicks_counter,
                #                                                                self.driver)
                # try:
                # 	self.close_popup_okx()
                # except exceptions.ElementNotInteractableException:
                # 	self.driver.refresh()
                #
                except (exceptions.ElementNotInteractableException, exceptions.MoveTargetOutOfBoundsException, exceptions.NoSuchElementException) as x:
                    print('kakaka')
                    self._wrong_captcha_clicks_counter = self.check_retries_limit(self._wrong_captcha_clicks_counter,
                                                                                  self.driver)
                    self.close_popup_okx()
                    print(x)
                    print('retry captcha')
            
            return True
        
        except Exception as x:
            print(x)
            raise custom_exceptions.UnableToProceedNeedHumanAttention
    
    def send_code(self, code):
        for code_input, code_char in zip(self.code_inputs, code):
            code_input.send_keys(int(code_char))
        
        if self.driver.find_element(by=By.CSS_SELECTOR, value='a.okx-header-footer-overview'):
            return True
    
    def get_p2p_info(self):
        time.sleep(10)
        buy_crypto_dropdown = self.driver.find_element(by=By.CSS_SELECTOR, value='li.nav-buy')
        print(buy_crypto_dropdown)
        p2p_trading_link = self.driver.find_element(by=By.CSS_SELECTOR, value='a.okx-header-footer-p2p-trading')
        ActionChains(self.driver).move_to_element(buy_crypto_dropdown).pause(5).move_to_element(p2p_trading_link).click().perform()
        # self.driver.get(url=self.p2p_url)
        time.sleep(4)
        currency_dropdown = self.driver.find_elements(by=By.CSS_SELECTOR, value='div.currency-option-wrap')[1]
        currency_dropdown.click()
        currency_input = self.driver.find_element(by=By.CSS_SELECTOR, value='input.common-input')
        
        ActionChains(self.driver).move_to_element(currency_input).click().send_keys('byn').move_by_offset(0, 30).pause(1).click().perform()
        time.sleep(2)
        
        # # Open payments options dropdown
        # payment_option = self.driver.find_element(by=By.CSS_SELECTOR, value='div.payment-option')
        # payment_option.click()
        # time.sleep(1)
        # # Choose Bank transfer option only offers
        # # bank_transfer_option = self.driver.find_element(by=By.XPATH,
        # #                          value='//*[@id="popup-1679320087792"]/div/div/div/div/div[2]/div[2]/div/div/div[2]')
        #
        # ActionChains(self.driver).move_to_element(payment_option).click().send_keys('bank').pause(4).move_by_offset(0, 50).pause(5).click().perform()
        # time.sleep(2)
        
        all_offers_cards = self.driver.find_elements(by=By.CSS_SELECTOR, value='tr.market-table-tr')
        print(all_offers_cards)
        print('gogogo', all_offers_cards[0].get_attribute('innerHTML'))
        change_rate_min = float(re.search(
            r'>[123]\.\d\d<', all_offers_cards[0].get_attribute('innerHTML')).group()[1:-1])
        
        print(change_rate_min)
        
        for index, offer_card in enumerate(all_offers_cards):
            offer_card_html = offer_card.get_attribute('innerHTML')
            
            print('kakaka', offer_card_html)
            
            limits_list = re.search(
                r'<div class="show-item">(\d*,?\d*\.\d*-.*) BYN', offer_card_html).group(1).split('-')
            
            print(limits_list)
            
            limits_list = [float(x.replace(',', '')) for x in limits_list]
            
            if limits_list[0] < 20 < limits_list[1]:
                change_rate_for_card_with_suitable_limit = float(re.search(
                    r'>([123]\.\d\d).{,12}(\r\n|\r|\n)?.{,10}BYN', offer_card_html).group(1))
                
                print(change_rate_for_card_with_suitable_limit)
                
                # for character in change_rate_for_card_with_suitable_limit:
                #     if not character.isdigit() or character != '.':
                #         change_rate_for_card_with_suitable_limit = change_rate_for_card_with_suitable_limit.replace(character, '')
                
                # change_rate_for_card_with_suitable_limit = float(change_rate_for_card_with_suitable_limit)
                print(change_rate_for_card_with_suitable_limit)
        
                if change_rate_for_card_with_suitable_limit - change_rate_min < 0.20:
                    buy_buttons = self.driver.find_elements(by=By.CSS_SELECTOR, value='button.base-trade-btn')
                    # Clicking buy button in card with suitable limit
                    buy_buttons[index].click()
                    # Click show more button
                    self.driver.find_element(by=By.CSS_SELECTOR, value='span.more-tip').click()
                    time.sleep(4)
                    seller_remark = self.driver.find_element(by=By.CSS_SELECTOR, value='div.dialog-taker-remark').text
                    print(seller_remark)
                    buy_amount_input = self.driver.find_elements(by=By.CSS_SELECTOR, value='input.product-input')[0]
                    buy_amount_input.send_keys(Keys.CONTROL + "a")
                    buy_amount_input.send_keys(Keys.DELETE)
                    buy_amount_input.send_keys(40)
                    
                    buy_button = self.driver.find_elements(by=By.CSS_SELECTOR, value='button.taker-btn')[1]
                    buy_button.click()
                    
                    confirm_button = self.driver.find_element(by=By.CSS_SELECTOR, value='button.dialog-btn')[1]
                    confirm_button.click()
                    
                    messages = self.driver.find_elements(by=By.CSS_SELECTOR, value='span.mess')
                    
                    credentials = self.driver.find_elements(by=By.CSS_SELECTOR, value='span.item-value')
                    
                    card_number = credentials[3]
                    bank_name = credentials[4]
                    
                    # confirm_payment_button = self.driver.find_element(by=By.CSS_SELECTOR, value='button.detail-main-action')
                    return True
                    
        raise custom_exceptions.UnableToProceedNeedHumanAttention
