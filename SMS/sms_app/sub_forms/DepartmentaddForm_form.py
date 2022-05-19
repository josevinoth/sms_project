from django import forms
from ..models import Department_info

class DepartmentaddForm(forms.ModelForm):
    class Meta:
        model = Department_info
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(DepartmentaddForm, self).__init__(*args, **kwargs)
        self.fields['dept_status'].empty_label = "--Select--"