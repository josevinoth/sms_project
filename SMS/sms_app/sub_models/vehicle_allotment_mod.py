from django.db import models

from .driver_master_mod import DrivermasterInfo
from .vehicle_replacement_status_mod import Replacementstatus
from ..models import EnquirynoteInfo,MyUser,VehiclemasterInfo,VehicletypeInfo,OwnershipInfo,Vendor_info,StatusList

class Vehicle_allotmentInfo(models.Model):
    va_enquirynumber = models.ForeignKey(EnquirynoteInfo, on_delete=models.PROTECT)
    va_vehiclesource = models.ForeignKey(OwnershipInfo, on_delete=models.CASCADE)
    va_vehicletype = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE,related_name='va_vehicletype', db_column='va_vehicletype')
    va_vehicletype_placed = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE,related_name='va_vehicletype_placed', db_column='va_vehicletype_placed')
    va_vehicletype_selection_requested= models.BooleanField(blank=True,null=True)
    va_vehicletype_selection_placed= models.BooleanField(blank=True,null=True)
    va_vehiclenumber = models.ForeignKey(VehiclemasterInfo, on_delete=models.CASCADE, null=True,blank=True)
    va_vehiclenumber_mkt = models.CharField(max_length=30,null=True,blank=True)
    va_drivername = models.CharField(max_length=100,null=True,blank=True)
    va_driver_lic = models.CharField(max_length=100,null=True,blank=True)
    va_driver_lic_expiry = models.CharField(max_length=100,null=True,blank=True)
    va_drivernumber = models.CharField(null=True,blank=True)
    va_updated_at = models.DateTimeField(null=True, auto_now=True)
    va_created_at = models.DateTimeField(null=True, auto_now_add=True)
    va_updated_by = models.ForeignKey(MyUser, related_name='va_updated_by', db_column='va_updated_by',on_delete=models.CASCADE, null=True)
    va_remarks=models.TextField(max_length=300,blank=True, null=True)
    va_vendor = models.ForeignKey(Vendor_info,on_delete=models.CASCADE, default='',blank=True, null=True)
    va_sale = models.FloatField(max_length=100,null=True,blank=True)
    va_special_sale = models.FloatField(max_length=100,null=True,blank=True)
    # va_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6,blank=True,null=True)
    va_status = models.ForeignKey(Replacementstatus, on_delete=models.CASCADE, default=1,blank=True,null=True)
    va_profit_percentage = models.FloatField(null=True, blank=True)
    va_standardbuy = models.FloatField(max_length=100, null=True, blank=True)
    va_specialbuy = models.FloatField(max_length=100, null=True, blank=True)
    va_driver = models.ForeignKey(DrivermasterInfo,on_delete=models.CASCADE,related_name='driver_name',null=True, blank=True)
    va_driver_master_id = models.IntegerField(null=True, blank=True)
    va_email_sent = models.BooleanField(default=False)
    va_replacement_reason = models.TextField(null=True, blank=True)
    va_replacement_date = models.DateTimeField(null=True, blank=True)
    va_replaced_allotment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replacement_chain')

    def __str__(self):
            if self.va_vehiclenumber and str(self.va_vehiclenumber):
                return str(self.va_vehiclenumber)
            return "Unknown vehicle"