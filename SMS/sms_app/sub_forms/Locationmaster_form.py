from django import forms
from ..models import LocationMaster

class LocationMasterForm(forms.ModelForm):
    class Meta:
        model = LocationMaster
        fields = ['location_name', 'state', 'latitude', 'longitude']
        widgets = {
            'location_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Start typing a location...',
                'id': 'autocomplete'
            }),
            'latitude': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'id': 'latitude'
            }),
            'longitude': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'id': 'longitude'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'id': 'state'
            }),
        }
