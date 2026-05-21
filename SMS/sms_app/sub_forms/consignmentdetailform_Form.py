from django import forms


from ..models import ConsignmentdetailInfo

class ConsignmentdetailaddForm(forms.ModelForm):
    co_cusrefnum_check = forms.BooleanField(required=False)
    co_cusrefnum = forms.CharField(required=False)

    class Meta:
        model = ConsignmentdetailInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ConsignmentdetailaddForm, self).__init__(*args, **kwargs)
        
        # Limit co_enquirynumber queryset to only the selected/active record to avoid querying and rendering 6,759 options
        enq_id = None
        if self.instance and self.instance.co_enquirynumber_id:
            enq_id = self.instance.co_enquirynumber_id
        elif 'initial' in kwargs and 'co_enquirynumber' in kwargs['initial']:
            enq_id = kwargs['initial']['co_enquirynumber']
        elif hasattr(self, 'data') and self.data and self.data.get('co_enquirynumber'):
            try:
                enq_id = int(self.data.get('co_enquirynumber'))
            except (ValueError, TypeError):
                pass
                
        if enq_id:
            self.fields['co_enquirynumber'].queryset = self.fields['co_enquirynumber'].queryset.filter(id=enq_id)
        else:
            self.fields['co_enquirynumber'].queryset = self.fields['co_enquirynumber'].queryset.none()
            
        # Limit co_customer queryset to only the selected/active record to avoid querying and rendering hundreds of options
        cust_id = None
        if self.instance and self.instance.co_customer_id:
            cust_id = self.instance.co_customer_id
        elif 'initial' in kwargs and 'co_customer' in kwargs['initial']:
            cust_id = kwargs['initial']['co_customer']
        elif hasattr(self, 'data') and self.data and self.data.get('co_customer'):
            try:
                cust_id = int(self.data.get('co_customer'))
            except (ValueError, TypeError):
                pass
                
        if cust_id:
            self.fields['co_customer'].queryset = self.fields['co_customer'].queryset.filter(id=cust_id)
        else:
            self.fields['co_customer'].empty_label = "--Select--"
            self.fields['co_customer'].queryset = self.fields['co_customer'].queryset.filter(cu_name__icontains='(T)')
            
        # Hide co_lastmodifiedby to avoid rendering options for all users
        self.fields['co_lastmodifiedby'].widget = forms.HiddenInput()
        
        # Empty out unused/unrendered foreign key querysets to save DB query and HTML rendering overhead
        self.fields['co_fromlocaion'].queryset = self.fields['co_fromlocaion'].queryset.none()
        self.fields['co_tolocation'].queryset = self.fields['co_tolocation'].queryset.none()
        
        self.fields['co_status'].empty_label = "--Select--"
        self.fields['co_cusrefnum'].empty_label = "--Select--"
        self.fields['co_gst_payable_by'].empty_label = "--Select--"


