# from django import forms
# from ..models import Employee
#
# class EmployeeaddForm(forms.ModelForm):
#     class Meta:
#         model = Employee
#         fields = '__all__'

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ..models import User_extInfo,Employee
from django import forms

class EmployeeaddForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'

class EmpeditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','is_active','email','password']

class UserexteditForm(forms.ModelForm):
    class Meta:
        model = User_extInfo
        fields = ['department','emp_contact','emp_designation','emp_branch','emp_role','emp_DOB','emp_DOJ','emp_pan','emp_uan','emp_esi','emp_aadhar','emp_organisation']
        # fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(UserexteditForm,self).__init__(*args, **kwargs)
        self.fields['emp_designation'].empty_label = "--Select--"
        self.fields['emp_branch'].empty_label = "--Select--"
        self.fields['emp_role'].empty_label = "--Select--"
        self.fields['department'].empty_label = "--Select--"
        self.fields['emp_organisation'].empty_label = "--Select--"
        self.fields['emp_DOB'].required = False
        self.fields['emp_DOJ'].required = False
        self.fields['emp_pan'].required = False
        self.fields['emp_uan'].required = False
        self.fields['emp_esi'].required = False
        self.fields['emp_aadhar'].required = False

