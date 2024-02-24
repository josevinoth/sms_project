from django.db import models
from ..models import Location_info,UnitInfo

class Packingjobs(models.Model):
    pj_s_no = models.CharField(blank=True, null=True,max_length=100, default='')
    pj_date = models.CharField(blank=True, null=True,max_length=100, default='')
    pj_job_no = models.CharField(blank=True, null=True,max_length=100, default='')
    pj_customer=models.CharField(blank=True, null=True,max_length=100, default='')
    pj_pack_type=models.CharField(blank=True, null=True,max_length=100, default='')
    pj_no_box=models.CharField(blank=True, null=True,max_length=100, default='')
    pj_reference=models.CharField(blank=True, null=True,max_length=100, default='')
    pj_bill_amount=models.CharField(blank=True, null=True,max_length=100, default='')
    pj_expense=models.CharField(blank=True, null=True,max_length=100, default='')

    class Meta:
        ordering = ["pj_s_no"]

    def __str__(self):
        return self.pj_s_no