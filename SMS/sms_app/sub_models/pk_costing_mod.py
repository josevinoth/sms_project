from django.db import models
from ..models import MyUser,Costtype,Costdescription,Natypeofwood,Unitofmeasure,PkneedassessmentInfo

class PkcostingInfo(models.Model):
    ct_cost_type = models.ForeignKey(Costtype, on_delete=models.CASCADE, default='')
    ct_cost_description = models.ForeignKey(Costdescription, on_delete=models.CASCADE, default='')
    ct_width = models.FloatField(blank=True, null=True, default=0.0)
    ct_height = models.FloatField(blank=True, null=True,default=0.0)
    ct_cft = models.FloatField(blank=True, null=True,default=0.0)
    ct_rate = models.FloatField(blank=True, null=True,default=0.0)
    ct_days= models.IntegerField(blank=True, null=True,default=0)
    ct_total_cost = models.FloatField(blank=True, null=True,default=0.0)
    ct_created_at = models.DateField(null=True, auto_now_add=True)
    ct_updated_at = models.DateField(null=True, auto_now=True)
    ct_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='ct_updated_by',db_column='ct_updated_by', null=True)
    ct_type_of_wood = models.ForeignKey(Natypeofwood, on_delete=models.CASCADE, default='',blank=True, null=True)
    ct_quantity= models.IntegerField(blank=True, null=True,default=0)
    ct_size=models.FloatField(blank=True, null=True,default=0.0)
    ct_uom = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE, default='',blank=True, null=True)
    ct_assessment_num=models.ForeignKey(PkneedassessmentInfo, on_delete=models.CASCADE, default='',blank=True, null=True)

    class Meta:
        ordering = ["ct_cost_type"]

    def __str__(self):
        return self.ct_cost_type