import os
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from dotenv import load_dotenv
from cryptoautobuy.selenium import gmail, exchange, main
from .services import AutoBuyExecutor
from cryptoautobuy.selenium import custom_exceptions
from django.core.mail import send_mail

load_dotenv('../.env')


def send_error_log_to_mail(exception):
    send_mail('Cryptoautobuy error', f'Возникла ошибка при работе...', os.getenv('EMAIL_HOST_USER'),
              ['dmitriyseur@gmail.com'], fail_silently=False)


def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)


# def handler403(request, exception=None):
#     if isinstance(exception, Ratelimited):
#         return JsonResponse({'text': 'banned', 'message': 'Вы превысили допустимый лимит запросов'})
#     return HttpResponseForbidden('Forbidden')


class InstructionView(View):
    template_name = 'instruction.html'
    
    def get(self, request, **kwargs):
        return render(request, self.template_name, {})


class AutoBuyExecuteView(View):
    def post(self, request, **kwargs):
        executor = AutoBuyExecutor('bank', 'exchange')
        try:
            if executor.login_to_exchange():
                return redirect('get-code-for-exchange')
        #     if executor.login_to_bank():
        #         if executor.login_to_exchange():
        #             return redirect('get-code-for-exchange')
        
        except custom_exceptions.UnableToProceedNeedHumanAttention:
            pass
     
     
class GetCodeForExchange(View):
    template_name = 'get_code_for_exchange.html'
    
    def get(self, request, **kwargs):
        return render(request, self.template_name, {})
    
    def post(self, request, **kwargs):
        code = request.POST.get('code')
        executor = AutoBuyExecutor.get_instance()
        executor.send_code_to_exc(code)
        executor.get_p2p_info_from_exc()
        
        
