from django import forms
from ..models import IncidentReportInfo

class IncidentReportForm(forms.ModelForm):
    class Meta:
        model = IncidentReportInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(IncidentReportForm, self).__init__(*args, **kwargs)
        self.fields['inc_branch'].empty_label = "--Select--"
        self.fields['inc_unit'].empty_label = "--Select--"
        self.fields['inc_customer'].empty_label = "--Select--"
        self.fields['inc_details'].empty_label = "--Select--"
        self.fields['inc_status'].empty_label = "--Select--"
        self.fields['inc_approval_status'].empty_label = "--Select--"