from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.forms import ValidationError

class LoginForm(AuthenticationForm):
    # username = forms.CharField()
    # password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password','required': True}))
    pass

class SignUpForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']

    def clean(self):
        cleaned_data = super().clean()

        if  User.objects.filter(username=cleaned_data.get('username')).exists():
            raise ValidationError('A user with that email is already registered.')
        
        return cleaned_data
