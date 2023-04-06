from cryptoautobuy.selenium import exchange, main, custom_exceptions


class AutoBuyExecutor:
	__instance = None
	
	@staticmethod
	def get_instance():
		if AutoBuyExecutor.__instance is None:
			raise Exception('U have skipped execution part')
		return AutoBuyExecutor.__instance
	
	def __init__(self, bank_name, exchange_name):
		if AutoBuyExecutor.__instance is not None:
			raise Exception('Can not create multiple instances for singleton class')
		AutoBuyExecutor.__instance = self
		self.bank = bank_name
		self.exchange = exchange_name
		self.bank_handler = main.BelinvestBankHandler()
		self.exchange_handler = exchange.OKXExchangeHandler()

	def __del__(self):
		AutoBuyExecutor.__instance = None
		print('instance = none')
		
	def UnableToProceedNeedHumanAttention_exception_handler(self):
		self.bank_handler.driver.close()
		self.exchange_handler.driver.close()
		self.__instance = None
		del self
		return False
	
	def login_to_bank(self):
		try:
			return self.bank_handler.login()
		except custom_exceptions.UnableToProceedNeedHumanAttention:
			return self.UnableToProceedNeedHumanAttention_exception_handler()
	
	def login_to_exchange(self):
		try:
			return self.exchange_handler.login_to_exchange()
		except custom_exceptions.UnableToProceedNeedHumanAttention:
			return self.UnableToProceedNeedHumanAttention_exception_handler()
		
	def send_code_to_exc(self, code):
		try:
			return self.exchange_handler.send_code(code)
		except custom_exceptions.UnableToProceedNeedHumanAttention:
			return self.UnableToProceedNeedHumanAttention_exception_handler()
		
	def get_p2p_info_from_exc(self):
		try:
			return self.exchange_handler.get_p2p_info()
		except custom_exceptions.UnableToProceedNeedHumanAttention:
			return self.UnableToProceedNeedHumanAttention_exception_handler()
		