# forms.py
from django import forms

class IncidentEmailForm(forms.Form):
    recipient = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Customer Email'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Message'}))
