from django.db import models
from ..models import PkpurchaseorderInfo,Unitofmeasure,Natypeofreq,Pkstocktype,Stockdescription,PkneedassessmentInfo,MyUser

class POdimension(models.Model):
    pod_assess_num = models.ForeignKey(PkneedassessmentInfo, on_delete=models.CASCADE, default='')
    pod_length = models.FloatField(default=0.0)
    pod_width = models.FloatField(default=0.0)
    pod_height = models.FloatField(default=0.0)
    pod_quantity = models.IntegerField(default=0)
    pod_created_at = models.DateTimeField(null=True, auto_now_add=True)
    pod_updated_at = models.DateTimeField(null=True, auto_now=True)
    pod_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='pod_updated_by',db_column='pod_updated_by')
    pod_wood_type = models.ForeignKey(Pkstocktype, on_delete=models.CASCADE,limit_choices_to={'id__in': [1, 4]})
    pod_wood_description = models.ForeignKey(Stockdescription, on_delete=models.CASCADE, default='',blank=True,null=True)
    pod_job_weight = models.FloatField( default=0.0)
    pod_type_of_req = models.ForeignKey(Natypeofreq, on_delete=models.CASCADE)
    pod_uom = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE, default='', limit_choices_to={'id__in': [1,2,3,4]},blank=True,null=True)
    pod_plywood_thickness = models.FloatField(default=0.0)
    pod_cost_unit=models.FloatField(default=0.0,null=True,blank=True)
    pod_cost_total=models.FloatField(default=0.0,null=True,blank=True)
    pod_item=models.CharField(max_length=100)
    pod_po_num = models.ForeignKey(PkpurchaseorderInfo, on_delete=models.CASCADE, blank=True,null=True)
    pod_delivery_schedule_date = models.DateField(blank=True, null=True)
    class Meta:
        ordering = ["pod_assess_num"]

    def __str__(self):
        return str(self.pod_item)