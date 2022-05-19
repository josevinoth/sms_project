from django import forms
from ..models import AssetInfo

class EmployeeaddForm(forms.ModelForm):
    class Meta:
        model = AssetInfo
        fields = '__all__'