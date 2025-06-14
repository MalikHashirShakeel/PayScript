from django import forms
from django.contrib.auth.forms import AuthenticationForm

class SimpleAuthenticationForm(AuthenticationForm):
    destination = forms.ChoiceField(
        choices=[('admin', 'Admin Panel'), ('dashboard', 'Dashboard')],
        widget=forms.RadioSelect(attrs={'class': 'hidden'}),
        initial='dashboard'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)