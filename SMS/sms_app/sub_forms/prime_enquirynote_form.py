from django import forms
from ..models import PrimeEnquirynoteInfo

class PrimeEnquirynoteaddForm(forms.ModelForm):

    class Meta:
        model = PrimeEnquirynoteInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PrimeEnquirynoteaddForm,self).__init__(*args, **kwargs)
        self.fields['pen_customername'].empty_label = "--Select--"
        self.fields['pen_customerdepartment'].empty_label = "--Select--"
        self.fields['pen_assignedto'].empty_label = "--Select--"
        self.fields['pen_status'].empty_label = "--Select--"
        self.fields['pen_fromlocaion'].empty_label = "--Select--"
        self.fields['pen_tolocation'].empty_label = "--Select--"
        self.fields['pen_touchpoint'].empty_label = "--Select--"
        self.fields['pen_touchpoint2'].empty_label = "--Select--"
        self.fields['pen_touchpoint3'].empty_label = "--Select--"
        self.fields['pen_touchpoint4'].empty_label = "--Select--"
        self.fields['pen_business_type'].empty_label = "--Select--"
        self.fields['pen_movement_type'].empty_label = "--Select--"
        self.fields['pen_trip_type'].required = False
