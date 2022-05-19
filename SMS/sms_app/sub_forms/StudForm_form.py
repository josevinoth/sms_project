from django import forms
from ..models import Stud_reg

class StudaddForm(forms.ModelForm):
    class Meta:
        model = Stud_reg
        fields = '__all__'
