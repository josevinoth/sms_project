from django import forms
from django.db.models import Q
from django.utils import timezone
from ..models import Sales_target_info, MyUser

class SalestargetaddForm(forms.ModelForm):
    class Meta:
        model = Sales_target_info
        fields = [
            'st_sales_person',
            'st_start_date',
            'st_end_date',
            'st_target_calls',
            'st_target_customers_onboard',
            'st_target_customers_new',
            'st_target_customers_existing',
            'st_target_revenue_new',
            'st_target_revenue_existing',
            'st_company',
            'st_remarks',
            'st_target_revenue',
            'st_target_customer',
            'st_updated_by',
        ]
        widgets = {
            'st_start_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'st_end_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(SalestargetaddForm, self).__init__(*args, **kwargs)
        if 'st_sales_person' in self.fields:
            # Show active users belonging to the Sales department
            sales_dept_q = Q(user_extinfo__department__dept_name__icontains='sales', is_active=True)
            if self.instance and self.instance.pk and self.instance.st_sales_person_id:
                sales_dept_q |= Q(pk=self.instance.st_sales_person_id)

            self.fields['st_sales_person'].queryset = MyUser.objects.filter(sales_dept_q).distinct().order_by('first_name')
            self.fields['st_sales_person'].empty_label = "--Select Sales Executive--"
            self.fields['st_sales_person'].required = True
        if 'st_start_date' in self.fields:
            self.fields['st_start_date'].required = True
        if 'st_end_date' in self.fields:
            self.fields['st_end_date'].required = True
        if 'st_company' in self.fields:
            self.fields['st_company'].empty_label = "--Select Company / Division (Optional)--"
            self.fields['st_company'].required = False
        if 'st_target_revenue' in self.fields:
            self.fields['st_target_revenue'].required = False
        if 'st_target_customer' in self.fields:
            self.fields['st_target_customer'].required = False
        if 'st_updated_by' in self.fields:
            self.fields['st_updated_by'].required = False

    def clean(self):
        cleaned_data = super(SalestargetaddForm, self).clean()
        sales_person = cleaned_data.get('st_sales_person')
        start_date = cleaned_data.get('st_start_date')
        end_date = cleaned_data.get('st_end_date')

        if start_date and end_date and start_date > end_date:
            self.add_error('st_end_date', "Target End Date cannot be earlier than Start Date.")

        if sales_person:
            today = timezone.now().date()
            qs = Sales_target_info.objects.filter(st_sales_person=sales_person)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            # Check for existing target whose end date is not expired (>= today, or >= start_date)
            unexpired = qs.filter(st_end_date__gte=today).order_by('-st_end_date').first()
            if not unexpired and start_date:
                unexpired = qs.filter(st_end_date__gte=start_date).order_by('-st_end_date').first()

            if unexpired:
                end_str = unexpired.st_end_date.strftime('%d-%m-%Y') if unexpired.st_end_date else ''
                msg = f"The target which is previously given doesn't reached the end date (Ends on {end_str})."
                self.add_error('st_sales_person', msg)
                raise forms.ValidationError(msg)

        return cleaned_data

