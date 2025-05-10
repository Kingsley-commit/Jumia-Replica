from django.shortcuts import render, redirect
from django.views.generic import CreateView, FormView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from django.contrib.auth.models import User

class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'account/auth.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        validated_data = form.cleaned_data
        user = authenticate(
                self.request,
                username=validated_data.get('username'),
                password=validated_data.get('password')
            )
        if user is None:
            raise ValidationError('This user does not exist')
        print(user)
        # login(self.request, user)
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super(LoginView, self).form_valid(form)


class RegistrationView(FormView):
    template_name = 'account/register.html'
    form_class = SignUpForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        user = User.objects.create_user(
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
            )
        user.save()
        # login(self.request, user)
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super(RegistrationView, self).form_valid(form)


class Logout(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')

