from django.db import models
from ..models import Tr_triptype_Info,CustomerInfo


class Haltingcharges(models.Model):
    hc_Customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, default='')
    hc_trip_type = models.ForeignKey(Tr_triptype_Info, on_delete=models.CASCADE, default="",null=True,blank=True)
    hc_charges = models.FloatField(max_length=10,default = '')

    class Meta:
        ordering = ["hc_Customer_name"]

    def __str__(self):
        return self.hc_Customer_name
