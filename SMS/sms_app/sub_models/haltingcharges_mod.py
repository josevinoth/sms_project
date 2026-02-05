from django.db import models
from ..models import Tr_triptype_Info,CustomerInfo, MyUser


class Haltingcharges(models.Model):
    hc_Customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, default='')
    hc_trip_type = models.ForeignKey(Tr_triptype_Info, on_delete=models.CASCADE, default="",null=True,blank=True)
    hc_charges = models.FloatField(max_length=10,default = '')
    hc_updated_at = models.DateTimeField(null=True, auto_now=True)
    hc_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ["hc_Customer_name"]

    def __str__(self):
        return self.hc_Customer_name
