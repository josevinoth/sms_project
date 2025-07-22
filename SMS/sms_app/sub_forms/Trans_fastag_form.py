from django import forms

class trans_fastag_form(forms.Form):
    vehicleNumber = forms.CharField(label="Vehicle Number", max_length=15)
    contactNumber = forms.CharField(label="Contact Number", max_length=15)
    fromDate = forms.DateTimeField(label="From Date & Time", required=True, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    toDate = forms.DateTimeField(label="To Date & Time", required=True, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
