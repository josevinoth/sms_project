from django.db import models
from ..models import EnquirynoteInfo,ConsignmentdetailInfo,MyUser,VehiclemasterInfo,VehicletypeInfo,OwnershipInfo

class Vehicle_allotmentInfo(models.Model):
    va_enquirynumber = models.ForeignKey(EnquirynoteInfo, on_delete=models.CASCADE, default='')
    va_consignmentnumber = models.ForeignKey(ConsignmentdetailInfo, on_delete=models.CASCADE, default='')
    va_vehiclesource = models.ForeignKey(OwnershipInfo, on_delete=models.CASCADE)
    va_vehicletype = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE,related_name='va_vehicletype', db_column='va_vehicletype')
    va_vehicletype_placed = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE,related_name='va_vehicletype_placed', db_column='va_vehicletype_placed')
    va_vehicletype_selection_requested= models.BooleanField(blank=True,null=True)
    va_vehicletype_selection_placed= models.BooleanField(blank=True,null=True)
    va_vehiclenumber = models.ForeignKey(VehiclemasterInfo, on_delete=models.CASCADE, null=True,blank=True)
    va_drivername = models.CharField(max_length=30,null=True,blank=True)
    va_driver_lic = models.CharField(max_length=100,null=True,blank=True)
    va_driver_lic_expiry = models.CharField(max_length=100,null=True,blank=True)
    va_drivernumber = models.CharField(max_length=30,null=True,blank=True)
    va_updated_at = models.DateTimeField(null=True, auto_now=True)
    va_created_at = models.DateTimeField(null=True, auto_now_add=True)
    va_updated_by = models.ForeignKey(MyUser, related_name='va_updated_by', db_column='va_updated_by',on_delete=models.CASCADE, null=True)
    va_remarks=models.TextField(max_length=300,blank=True, null=True)

    def __str__(self):
        return self.va_vehiclenumber