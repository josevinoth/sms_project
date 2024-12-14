from django.db import models
from ..models import CustomerInfo

class DsrInfo(models.Model):
    ds_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True,null=True)
    def __str__(self):
        return f"high value check at {self.ds_customer}"