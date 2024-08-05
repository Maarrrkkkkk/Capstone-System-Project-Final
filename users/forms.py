from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=150, required=True, help_text='Required')
    firstname = forms.CharField(max_length=30, required=True, help_text='Required')
    middlename = forms.CharField(max_length=30, required=False, help_text='Optional')
    lastname = forms.CharField(max_length=30, required=True, help_text='Required')
    email = forms.EmailField(max_length=254, required=True, help_text='Required')

    class Meta:
        model = CustomUser
        fields = ('username', 'firstname', 'middlename', 'lastname', 'email', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):
    username = forms.CharField(max_length=150, required=True, help_text='Required')
    firstname = forms.CharField(max_length=30, required=True, help_text='Required')
    middlename = forms.CharField(max_length=30, required=False, help_text='Optional')
    lastname = forms.CharField(max_length=30, required=True, help_text='Required')
    email = forms.EmailField(max_length=254, required=True, help_text='Required')

    class Meta:
        model = CustomUser
        fields = ('username', 'firstname', 'middlename', 'lastname', 'email')

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter your Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your Password'}))

class CustomAuthenticationForm(AuthenticationForm):
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'last_name', 'first_name', 'middle_name', 'email']
        help_texts = {
            'username': None,
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

# class CustomPasswordChangeForm(PasswordChangeForm):
#     old_password = forms.CharField(
#         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your old password'})
#     )
#     new_password1 = forms.CharField(
#         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your new password'})
#     )
#     new_password2 = forms.CharField(
#         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your new password'})
#     )

