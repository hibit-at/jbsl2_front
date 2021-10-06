from django import forms
from .models import Player

class KeywordForm(forms.Form):
    keyword = forms.CharField(label='keyword', max_length=20)