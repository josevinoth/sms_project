from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import HiddenInput

from ..models import User_extInfo
from django import forms

class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=False)
    class Meta:
        model = User
        fields = ('username','first_name','last_name','is_active','email','password1','password2')
        # fields = '__all__'
class UserextForm(forms.ModelForm):
    emp_contact = forms.CharField(required=False)
    class Meta:
        model = User_extInfo
        fields = ['emp_contact']
        # fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(UserextForm,self).__init__(*args, **kwargs)
        # self.fields['emp_designation'].empty_label = "--Select--"
        # self.fields['emp_branch'].empty_label = "--Select--"
        # self.fields['emp_role'].empty_label = "--Select--"
        # self.fields['department'].empty_label = "--Select--"