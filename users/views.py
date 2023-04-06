from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.views import View
from . import forms


# Create your views here.

class RegisterView(View):
	template_name = 'registration/register.html'
	
	def get(self, request):
		context = {
			'form': forms.UserCreateForm(),
		}
		return render(request, self.template_name, context)
	
	def post(self, request):
		form = forms.UserCreateForm(request.POST)
		
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password1')
			user = authenticate(email=email, password=password)
			login(request, user)
			return redirect('instruction')
		
		context = {
			'form': form,
		}
		
		return render(request, self.template_name, context)


class LoginView(View):
	template_name = 'registration/login.html'
	
	def get(self, request):
		context = {
			'form': forms.UserLoginForm(),
		}
		return render(request, self.template_name, context)
	
	def post(self, request):
		form = forms.UserLoginForm(request.POST)
		
		if form.is_valid():
			user = form.get_user()
			login(request, user)
			
			nexty = request.POST.get('next')
			if nexty:
				try:
					return HttpResponseRedirect(nexty)
				except:
					raise Http404
		
		context = {
			'form': form
		}
		
		return render(request, self.template_name, context)
	