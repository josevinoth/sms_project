# forms.py
from django import forms

class trans_fastag_form(forms.Form):
    vehicleNumber = forms.CharField(label="Vehicle Number", required=False, max_length=20)
    contactNumber = forms.CharField(label="Contact Number", required=False, max_length=15)
    fromDate = forms.DateField(label="From Date", widget=forms.DateInput(attrs={'type': 'date'}))
    toDate = forms.DateField(label="To Date", widget=forms.DateInput(attrs={'type': 'date'}))
