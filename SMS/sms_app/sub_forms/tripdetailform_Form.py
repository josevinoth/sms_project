from django import forms
from ..models import TripdetailInfo

class TripdetailaddForm(forms.ModelForm):

    class Meta:
        model = TripdetailInfo
        fields = '__all__'
        # fields = ['tr_enquirynumber', 'tr_consignmentnumber', 'tr_tripnumber', 'tr_transportbusinesstype',
        #           'tr_vehiclesource', 'tr_vehicletype', 'tr_vehiclenumber', 'tr_drivername', 'tr_drivernumber',
        #           'tr_fromlocation', 'tr_startingkm', 'tr_startingdate', 'tr_sealnumber', 'tr_containernumber',
        #           'tr_tolocation', 'tr_endingkm', 'tr_endingdate', 'tr_status', 'tr_updated_by']

    def __init__(self, *args, **kwargs):
        super(TripdetailaddForm,self).__init__(*args, **kwargs)
        self.fields['tr_consignmentnumber'].empty_label = "--Select--"
        self.fields['tr_vehiclesource'].empty_label = "--Select--"
        self.fields['tr_transportbusinesstype'].empty_label = "--Select--"
        self.fields['tr_vehicletype'].empty_label = "--Select--"
        self.fields['tr_vehiclenumber'].empty_label = "--Select--"
        self.fields['tr_fromlocation'].empty_label = "--Select--"
        self.fields['tr_tolocation'].empty_label = "--Select--"
        self.fields['tr_status'].empty_label = "--Select--"