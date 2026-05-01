from django.db import models
from .driver_master_mod import DrivermasterInfo
from .location_info_mod import Location_info

class DriverSalaryInfo(models.Model):
    ds_driverid = models.ForeignKey(DrivermasterInfo, on_delete=models.CASCADE, db_column='driver_id')
    ds_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, null=True, blank=True, db_column='branch_id')
    ds_driver_name = models.CharField(max_length=255, null=True, blank=True, db_column='driver_name')
    ds_month = models.DateField(db_column='month')
    ds_monthly_salary = models.FloatField(default=0.0, db_column='monthly_salary')

    class Meta:
        ordering = ["-ds_month", "ds_driverid__dm_name"]

    def __str__(self):
        return f"{self.ds_driverid.dm_name} - {self.ds_month.strftime('%Y-%m')}"
