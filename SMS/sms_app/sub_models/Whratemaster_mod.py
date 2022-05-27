from django.db import models
from ..models import WhstoragetypeInfo

class WhratemasterInfo(models.Model):
    whrm_customer_name = models.CharField(blank=True, null=True,max_length=20)
    whrm_storage_type = models.ForeignKey(WhstoragetypeInfo, on_delete=models.CASCADE, default='')
    whrm_storage_charge = models.IntegerField()
    whrm_loading_charge = models.IntegerField()
    whrm_unloading_charge = models.IntegerField()
    whrm_forkliftloading_charge = models.IntegerField()
    whrm_forkliftunloading_charge = models.IntegerField()
    whrm_crane_loading_charge = models.IntegerField()
    whrm_crane_unloading_charge = models.IntegerField()
    whrm_over_time_charge = models.IntegerField()
    whrm_insurance_charge = models.IntegerField()
    whrm_addmanpow_charge = models.IntegerField()