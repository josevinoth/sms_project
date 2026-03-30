from django.db import models
from .customer_mod import CustomerInfo
from .charge_type_mod import Charge_type
from .vehicletype_mod import VehicletypeInfo

class ChargeMasterInfo(models.Model):
    cm_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, null=True)
    cm_charge_type = models.ForeignKey(Charge_type, on_delete=models.CASCADE, null=True)
    cm_vehicle_type = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, null=True)
    cm_amount = models.FloatField(default=0.0)
    cm_created_at = models.DateTimeField(auto_now_add=True, null=True)
    cm_updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ["-cm_created_at"]

    def __str__(self):
        return f"{self.cm_customer} - {self.cm_charge_type}"
