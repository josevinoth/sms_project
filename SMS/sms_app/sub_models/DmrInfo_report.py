from django.db import models
from ..models import CustomerInfo

class DmrInfo(models.Model):
    dmr_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE)

    def __str__(self):
        return f"DMR report for {self.dmr_customer}"
