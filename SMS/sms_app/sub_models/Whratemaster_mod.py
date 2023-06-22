from django.db import models
from ..models import MyUser,VehicletypeInfo,CustomerInfo,CustomertypeInfo,TrbusinesstypeInfo,Wh_chargetype

class WhratemasterInfo(models.Model):
    whrm_customer_name = models.ForeignKey(CustomerInfo,on_delete=models.CASCADE, default='')
    whrm_businessmodel = models.ForeignKey(TrbusinesstypeInfo, on_delete=models.CASCADE, default='')
    whrm_charge_type = models.ForeignKey(Wh_chargetype, on_delete=models.CASCADE, default='')
    whrm_max_wt = models.FloatField(default=0.0)
    whrm_min_wt = models.FloatField(default=0.0)
    # whrm_item = models.FloatField(default=0.0)
    whrm_rate = models.FloatField(default=0.0)
    # whrm_total = models.FloatField(default=0.0)
    whrm_description = models.CharField(blank=True, null=True, max_length=20)
    whrm_updated_on = models.DateTimeField(null=True,auto_now=True)
    whrm_updated_by = models.ForeignKey(MyUser,on_delete=models.CASCADE, default='')
    whrm_vehicle_type = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, blank=True, null=True)
