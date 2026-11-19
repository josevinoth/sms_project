from django import forms
from ..models import NewCustomerMaster

class NewCustomerMasterForm(forms.ModelForm):
    class Meta:
        model = NewCustomerMaster
        fields = ['customer_name', 'is_active']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control form-control-modern',
                'placeholder': 'Enter Customer Name',
                'required': 'required',
                'id': 'customer_name',
                'autocomplete': 'off',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'custom-control-input',
                'id': 'is_active',
            }),
        }

    def clean_customer_name(self):
        name = self.cleaned_data.get('customer_name', '').strip()
        if not name:
            raise forms.ValidationError("Customer Name is required.")
        # Check uniqueness case-insensitively, excluding current instance
        qs = NewCustomerMaster.objects.filter(customer_name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Customer with name '{name}' already exists.")
        return name
