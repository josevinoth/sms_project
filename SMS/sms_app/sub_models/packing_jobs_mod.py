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
    pj_production_completed_flag = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')
    pj_material_returned_flag = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Yes', 'Yes'), ('No', 'No'), ('Returned', 'Returned')], default='Pending')
    pj_qc_completed_flag = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')

    class Meta:
        ordering = ["pj_s_no"]

    def __str__(self):
        return self.pj_s_no