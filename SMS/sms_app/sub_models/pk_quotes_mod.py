from django.db import models
from ..models import MyUser

class PkquotesInfo(models.Model):
    qt_quotes_num = models.CharField(max_length=100,null=True, blank=True)
    qt_date = models.DateField(blank=True, null=True)
    qt_item_value = models.FloatField(blank=True, null=True, default=0.0)
    qt_freight_charges = models.FloatField(blank=True, null=True, default=0.0)
    qt_handling_charges = models.FloatField(blank=True, null=True, default=0.0)
    qt_total = models.FloatField(blank=True, null=True, default=0.0)
    qt_created_at = models.DateField(null=True, auto_now_add=True)
    qt_updated_at = models.DateField(null=True, auto_now=True)
    qt_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='qt_updated_by',db_column='qt_updated_by', null=True)

    class Meta:
        ordering = ["qt_quotes_num"]

    def __str__(self):
        return self.qt_quotes_num