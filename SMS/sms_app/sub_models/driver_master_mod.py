from django.db import models
from ..models import OwnershipInfo,User

class DrivermasterInfo(models.Model):
    dm_vehiclesource = models.ForeignKey(OwnershipInfo, on_delete=models.CASCADE)
    dm_user_id = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    dm_name = models.CharField(max_length=100, default='')
    dm_id = models.CharField(max_length=100,null=True,blank=True)
    dm_drivernumber = models.CharField(null=True,blank=True)
    dm_driver_lic = models.CharField(max_length=100, null=True, blank=True)
    dm_driver_lic_expiry = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        ordering = ["dm_name"]

    def __str__(self):
        return self.dm_name