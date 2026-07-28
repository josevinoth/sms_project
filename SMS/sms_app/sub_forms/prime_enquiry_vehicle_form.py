from django import forms
from ..sub_models.prime_enquiry_vehicle_mod import PrimeEnquiryVehicle
from ..sub_models.prime_enquirynote_mod import PrimeEnquirynoteInfo


class PrimeEnquiryVehicleForm(forms.ModelForm):

    class Meta:
        model = PrimeEnquiryVehicle
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PrimeEnquiryVehicleForm, self).__init__(*args, **kwargs)
        self.fields['pev_enquirynumber'].empty_label = '--Booking Number--'
        # Now uses the dedicated PrimeEnquirynoteInfo model
        self.fields['pev_enquirynumber'].queryset = PrimeEnquirynoteInfo.objects.all()
        self.fields['pev_vehicletype'].empty_label = '--Vehicle Type--'
        self.fields['pev_vehiclecategory'].empty_label = '--Vehicle Category--'
        self.fields['pev_updated_by'].empty_label = '--Select--'
