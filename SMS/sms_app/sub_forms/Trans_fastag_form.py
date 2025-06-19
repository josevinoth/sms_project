from django import forms

class trans_fastag_form(forms.Form):
    vehicleNumber = forms.CharField(label="Vehicle Number", max_length=15)
    contactNumber = forms.CharField(label="Contact Number", max_length=15)
    fromDate = forms.DateField(label="From Date", widget=forms.DateInput(attrs={'type': 'date'}))
    toDate = forms.DateField(label="To Date", widget=forms.DateInput(attrs={'type': 'date'}))
