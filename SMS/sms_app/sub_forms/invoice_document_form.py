from django import forms
from ..models import InvoiceDocumentInfo, Tripstatusinfo


class InvoiceDocumentForm(forms.ModelForm):
    class Meta:
        model = InvoiceDocumentInfo
        fields = [
            'id_status',
            'id_trip_cost_doc',
            'id_parking_doc',
            'id_toll_doc',
            'id_loading_doc',
            'id_unloading_doc',
            'id_weighment_doc',
            'id_handling_doc',
            'id_pod_doc',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Trip Settled = id 7, Ready for Invoice = by name
        self.fields['id_status'].queryset = (
            Tripstatusinfo.objects.filter(id__in=[7]) |
            Tripstatusinfo.objects.filter(status='Ready for Invoice')
        )
        self.fields['id_status'].empty_label = '--Select Status--'
        self.fields['id_status'].label = 'Invoice Status'

        for field_name in self.fields:
            if field_name != 'id_status':
                self.fields[field_name].required = False
                self.fields[field_name].widget = forms.FileInput()
