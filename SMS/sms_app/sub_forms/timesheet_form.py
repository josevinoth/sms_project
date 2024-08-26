from django import forms
from ..models import timesheet_Info

class timesheetaddForm(forms.ModelForm):
    class Meta:
        model = timesheet_Info
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(timesheetaddForm,self).__init__(*args, **kwargs)
        self.fields['ts_application'].empty_label = "--Select--"
        self.fields['ts_developer'].empty_label = "--Select--"
        # self.fields['Bay_unit_name'].empty_label = "--Select--"