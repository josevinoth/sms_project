import datetime

from django.db import models
from ..models import MyUser

class PkpurchaseorderInfo(models.Model):
    po_num = models.CharField(max_length=100,null=True, blank=True)
    po_date = models.DateTimeField(blank=True, null=True)
    po_value = models.FloatField(blank=True, null=True, default=0.0)
    po_tax = models.FloatField(blank=True, null=True, default=0.0)
    po_total_value = models.FloatField(blank=True, null=True, default=0.0)
    po_validity_date = models.DateField(blank=True, null=True)
    po_delivery_schedule_date = models.DateField(blank=True, null=True)
    po_payment_terms = models.CharField(max_length=30,null=True, blank=True)
    po_created_at = models.DateField(null=True, auto_now_add=True)
    po_updated_at = models.DateField(null=True, auto_now=True)
    po_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='po_updated_by',db_column='po_updated_by', null=True)

    class Meta:
        ordering = ["po_num"]

    def __str__(self):
        return self.po_num

