from django import forms
from ..models import ExpenseInfo
from datetime import datetime, time


class ExpenseaddForm(forms.ModelForm):
    # Use DateInput widgets in the form and convert to datetime on save
    class Meta:
        model = ExpenseInfo
        fields = '__all__'
        widgets = {
            'exp_vendor_bill_date': forms.DateInput(attrs={'type': 'date'}),
            'exp_service_start_date': forms.DateInput(attrs={'type': 'date'}),
            'exp_service_end_date': forms.DateInput(attrs={'type': 'date'}),
            'exp_due_date': forms.DateInput(attrs={'type': 'date'}),
            'exp_paid_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(ExpenseaddForm, self).__init__(*args, **kwargs)
        # keep existing empty_label logic but guard if fields missing
        try:
            self.fields['exp_iou'].empty_label = "--Select--"
            self.fields['exp_vendor'].empty_label = "--Select--"
            self.fields['exp_expense_type'].empty_label = "--Select--"
            self.fields['exp_uom'].empty_label = "--Select--"
            self.fields['exp_category'].empty_label = "--Select--"
            self.fields['exp_business'].empty_label = "--Select--"
            self.fields['exp_credit_ledger'].empty_label = "--Select--"
        except Exception:
            pass

        # If an instance is passed, convert the model's datetime values to date strings for the widget
        if self.instance and getattr(self.instance, 'pk', None):
            for fld in ('exp_vendor_bill_date', 'exp_service_start_date', 'exp_service_end_date', 'exp_due_date', 'exp_paid_date'):
                val = getattr(self.instance, fld, None)
                if val:
                    try:
                        self.initial.setdefault(fld, val.date().isoformat())
                    except Exception:
                        pass

    def save(self, commit=True):
        # Convert cleaned date values to datetimes at midnight to satisfy the model DateTimeField
        instance = super(ExpenseaddForm, self).save(commit=False)
        for fld in ('exp_vendor_bill_date', 'exp_service_start_date', 'exp_service_end_date', 'exp_due_date', 'exp_paid_date'):
            value = self.cleaned_data.get(fld, None)
            if value:
                try:
                    dt = datetime.combine(value, time.min)
                    setattr(instance, fld, dt)
                except Exception:
                    setattr(instance, fld, value)
            else:
                setattr(instance, fld, None)
        if commit:
            instance.save()
            self.save_m2m()
        return instance
