# models.py
from django.db import models

from .driver_master_mod import DrivermasterInfo
from ..models import MyUser

class driver_settlement_info(models.Model):
    driver = models.ForeignKey(DrivermasterInfo,on_delete=models.CASCADE,related_name='driver_settlements',null=True, blank=True)
    driver_id_value = models.CharField(max_length=100,null=True, blank=True)
    driver_name = models.CharField(max_length=100,null=True, blank=True)
    driver_phone = models.CharField(max_length=10, null=True, blank=True)
    driver_licence = models.CharField(max_length=100, null=True, blank=True)
    ds_created_at = models.DateTimeField(null=True, auto_now_add=True)
    ds_updated_at = models.DateTimeField(null=True, auto_now=True)
    ds_updated_by = models.ForeignKey(MyUser, null=True, blank=True, on_delete=models.CASCADE, related_name='ds_updated_by', db_column='ds_updated_by')
    ds_tripadvance = models.FloatField(default=0.0)
    ds_tripexpense = models.FloatField(default=0.0)
    ds_balance = models.FloatField(default=0.0)
    driver_licence_expiry = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ["driver_name"]
        constraints = [
            models.UniqueConstraint(
                fields=['driver', 'driver_id_value', 'driver_licence'],
                name='unique_driver_settlement'
            )
        ]

    def __str__(self):
        return self.driver_name