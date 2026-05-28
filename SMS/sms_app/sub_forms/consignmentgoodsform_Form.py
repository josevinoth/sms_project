from django import forms
from ..models import ConsignmentgoodsInfo,Stock_type,ConsigneeInfo,ConsignerInfo


class ConsignmentgoodsaddForm(forms.ModelForm):

    class Meta:
        model = ConsignmentgoodsInfo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ConsignmentgoodsaddForm, self).__init__(*args, **kwargs)
        
        # Limit cg_consignmentnumber to only the current/active record to avoid querying and rendering 9,605 options
        cg_id = None
        if hasattr(self, 'data') and self.data and self.data.get('cg_consignmentnumber'):
            try:
                cg_id = int(self.data.get('cg_consignmentnumber'))
            except (ValueError, TypeError):
                pass
        if not cg_id and self.instance and self.instance.cg_consignmentnumber_id:
            cg_id = self.instance.cg_consignmentnumber_id
        elif not cg_id and 'initial' in kwargs and 'cg_consignmentnumber' in kwargs['initial']:
            cg_id = kwargs['initial']['cg_consignmentnumber']
                
        if cg_id:
            self.fields['cg_consignmentnumber'].queryset = self.fields['cg_consignmentnumber'].queryset.filter(id=cg_id)
        else:
            self.fields['cg_consignmentnumber'].queryset = self.fields['cg_consignmentnumber'].queryset.none()
            
        # Hide cg_lastmodifiedby to avoid rendering options for all users
        self.fields['cg_lastmodifiedby'].widget = forms.HiddenInput()
        
        self.fields['cg_consignmentnumber'].empty_label = "--Select--"
        self.fields['cg_currency_type'].empty_label = "--Select--"
        self.fields['cg_lastmodifiedby'].empty_label = "--Select--"
        self.fields['cg_consigner'].empty_label = "--Select--"
        self.fields['cg_consignee'].empty_label = "--Select--"
        self.fields['cg_description'].empty_label = "--Select--"
        self.fields['cg_description'].queryset = Stock_type.objects.all()
                # Limit cg_consigner queryset to only the selected/active record to avoid loading all options
        cg_consigner_id = None
        if hasattr(self, 'data') and self.data and self.data.get('cg_consigner'):
            try:
                cg_consigner_id = int(self.data.get('cg_consigner'))
            except (ValueError, TypeError):
                pass
        if not cg_consigner_id and self.instance and self.instance.cg_consigner_id:
            cg_consigner_id = self.instance.cg_consigner_id
        elif not cg_consigner_id and 'initial' in kwargs and 'cg_consigner' in kwargs['initial']:
            cg_consigner_id = kwargs['initial']['cg_consigner']
        if cg_consigner_id:
            self.fields['cg_consigner'].queryset = ConsignerInfo.objects.filter(id=cg_consigner_id)
        else:
            self.fields['cg_consigner'].queryset = ConsignerInfo.objects.none()

        # Limit cg_consignee queryset to only the selected/active record to avoid loading all options
        cg_consignee_id = None
        if hasattr(self, 'data') and self.data and self.data.get('cg_consignee'):
            try:
                cg_consignee_id = int(self.data.get('cg_consignee'))
            except (ValueError, TypeError):
                pass
        if not cg_consignee_id and self.instance and self.instance.cg_consignee_id:
            cg_consignee_id = self.instance.cg_consignee_id
        elif not cg_consignee_id and 'initial' in kwargs and 'cg_consignee' in kwargs['initial']:
            cg_consignee_id = kwargs['initial']['cg_consignee']
        if cg_consignee_id:
            self.fields['cg_consignee'].queryset = ConsigneeInfo.objects.filter(id=cg_consignee_id)
        else:
            self.fields['cg_consignee'].queryset = ConsigneeInfo.objects.none()
        self.fields['cg_consignmenttype'].empty_label = "--Select--"