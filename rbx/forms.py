from django import forms
from django.utils.translation import ugettext as _


class HomeSignupForm(forms.Form):
    name = forms.CharField(max_length=100, label='',
        widget=forms.TextInput(attrs={'placeholder': _('Your name')}))
    email = forms.EmailField(label='',
        widget=forms.TextInput(attrs={'placeholder': _('Your email address')}))
    password = forms.CharField(label='',
        widget=forms.PasswordInput(attrs={'placeholder': _('Pick a password')}))
