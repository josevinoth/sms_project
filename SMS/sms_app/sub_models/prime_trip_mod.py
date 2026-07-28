from django.db import models
from .prime_vehicle_allotment_mod import PrimeVehicleAllotmentInfo
from ..models import MyUser


class PrimeTripInfo(models.Model):
    pt_allotment = models.ForeignKey(PrimeVehicleAllotmentInfo, on_delete=models.CASCADE, related_name='prime_trips')
    pt_prime_trip_no = models.CharField(max_length=50, null=True, blank=True)
    
    pt_from_date = models.DateField(null=True, blank=True)
    pt_from_time = models.TimeField(null=True, blank=True)
    pt_from_km = models.IntegerField(null=True, blank=True)
    pt_from_place = models.CharField(max_length=200, null=True, blank=True)
    
    pt_to_date = models.DateField(null=True, blank=True)
    pt_to_time = models.TimeField(null=True, blank=True)
    pt_to_km = models.IntegerField(null=True, blank=True)
    pt_to_place = models.CharField(max_length=200, null=True, blank=True)
    
    pt_empty_shipment = models.CharField(max_length=50, choices=[('Empty', 'Empty'), ('Shipment', 'Shipment')], default='Shipment')
    
    pt_cnote_number = models.CharField(max_length=100, null=True, blank=True)
    pt_cnote_date = models.DateField(null=True, blank=True)
    pt_consigner = models.CharField(max_length=200, null=True, blank=True)
    pt_consignee = models.CharField(max_length=200, null=True, blank=True)
    pt_shipment_weight = models.FloatField(null=True, blank=True)
    pt_no_of_pcs = models.IntegerField(null=True, blank=True)
    pt_shipment_value_inr = models.FloatField(null=True, blank=True)
    
    pt_customer_ref_name = models.CharField(max_length=200, null=True, blank=True)
    pt_customer_ref_no = models.CharField(max_length=200, null=True, blank=True)
    pt_ewb_no = models.CharField(max_length=200, null=True, blank=True)
    pt_ewb_validity_date = models.DateField(null=True, blank=True)

    pt_created_at = models.DateTimeField(auto_now_add=True, null=True)
    pt_updated_at = models.DateTimeField(auto_now=True, null=True)
    pt_created_by = models.ForeignKey(MyUser, related_name='pt_created_by', on_delete=models.SET_NULL, null=True)
    pt_updated_by = models.ForeignKey(MyUser, related_name='pt_updated_by', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'PrimeTripInfo'

    @property
    def status(self):
        if self.pt_to_place or self.pt_to_km or self.pt_to_date:
            return "Trip Closed"
        return "Trip Started"

    def __str__(self):
        return f"{self.pt_prime_trip_no or 'New Prime Trip'} - {self.pt_allotment_id}"
