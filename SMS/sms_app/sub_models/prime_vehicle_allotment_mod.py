from django.db import models

from .driver_master_mod import DrivermasterInfo
from .vehicle_replacement_status_mod import Replacementstatus
from .prime_enquirynote_mod import PrimeEnquirynoteInfo
from ..models import MyUser, VehiclemasterInfo, VehicletypeInfo, OwnershipInfo, Vendor_info, StatusList

class PrimeVehicleAllotmentInfo(models.Model):
    pva_enquirynumber = models.ForeignKey(PrimeEnquirynoteInfo, on_delete=models.PROTECT)
    pva_vehiclesource = models.ForeignKey(OwnershipInfo, on_delete=models.CASCADE)
    pva_vehicletype = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, related_name='pva_vehicletype', db_column='pva_vehicletype')
    pva_vehicletype_placed = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, related_name='pva_vehicletype_placed', db_column='pva_vehicletype_placed')
    pva_vehicletype_selection_requested = models.BooleanField(blank=True, null=True)
    pva_vehicletype_selection_placed = models.BooleanField(blank=True, null=True)
    pva_prime_enquiry_vehicle = models.ForeignKey('PrimeEnquiryVehicle', on_delete=models.CASCADE, null=True, blank=True)
    pva_vehiclenumber = models.ForeignKey(VehiclemasterInfo, on_delete=models.CASCADE, null=True, blank=True)
    pva_vehiclenumber_mkt = models.CharField(max_length=30, null=True, blank=True)
    pva_drivername = models.CharField(max_length=100, null=True, blank=True)
    pva_driver_lic = models.CharField(max_length=100, null=True, blank=True)
    pva_driver_lic_expiry = models.CharField(max_length=100, null=True, blank=True)
    pva_drivernumber = models.CharField(null=True, blank=True)
    pva_updated_at = models.DateTimeField(null=True, auto_now=True)
    pva_created_at = models.DateTimeField(null=True, auto_now_add=True)
    pva_updated_by = models.ForeignKey(MyUser, related_name='pva_updated_by', db_column='pva_updated_by', on_delete=models.CASCADE, null=True)
    pva_remarks = models.TextField(max_length=300, blank=True, null=True)
    pva_vendor = models.ForeignKey(Vendor_info, on_delete=models.CASCADE, default='', blank=True, null=True)
    pva_sale = models.FloatField(max_length=100, null=True, blank=True)
    pva_status = models.ForeignKey(Replacementstatus, on_delete=models.CASCADE, default=1, blank=True, null=True)
    pva_profit_percentage = models.FloatField(null=True, blank=True)
    pva_standardbuy = models.FloatField(max_length=100, null=True, blank=True)
    pva_specialbuy = models.FloatField(max_length=100, null=True, blank=True)
    pva_driver = models.ForeignKey(DrivermasterInfo, on_delete=models.CASCADE, related_name='pva_driver_name', null=True, blank=True)
    pva_driver_master_id = models.IntegerField(null=True, blank=True)
    pva_original_vehiclenumber = models.ForeignKey(VehiclemasterInfo, on_delete=models.CASCADE, null=True, blank=True, related_name='pva_original_vehicle')
    pva_original_vehiclenumber_mkt = models.CharField(max_length=30, null=True, blank=True)
    pva_original_drivername = models.CharField(max_length=100, null=True, blank=True)
    pva_original_drivernumber = models.CharField(max_length=100, null=True, blank=True)
    pva_original_driver_lic = models.CharField(max_length=100, null=True, blank=True)
    pva_original_driver_lic_expiry = models.CharField(max_length=100, null=True, blank=True)
    pva_email_sent = models.BooleanField(default=False)
    pva_replacement_reason = models.TextField(null=True, blank=True)
    pva_replacement_date = models.DateTimeField(null=True, blank=True)
    pva_replaced_allotment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='pva_replacement_chain')
    
    pva_prime_job_number = models.CharField(max_length=50, null=True, blank=True)
    pva_prime_trip_no = models.CharField(max_length=50, null=True, blank=True)
    pva_prime_from_date = models.DateField(null=True, blank=True)
    pva_prime_from_time = models.TimeField(null=True, blank=True)
    pva_prime_from_km = models.FloatField(null=True, blank=True)

    def __str__(self):
        if self.pva_vehiclenumber and str(self.pva_vehiclenumber):
            return str(self.pva_vehiclenumber)
        return "Unknown vehicle"
