from django.db import models
from ..models import Pkstocktype,MyUser,Costtype,Stockdescription,Unitofmeasure,PkneedassessmentInfo

class PkretrivalInfo(models.Model):
    pret_cost_type = models.ForeignKey(Costtype, on_delete=models.CASCADE, default='')
    pret_stock_description = models.ForeignKey(Stockdescription, on_delete=models.CASCADE, blank=True,null=True)
    pret_width = models.FloatField(blank=True, null=True, default=0.0)
    pret_height = models.FloatField(blank=True, null=True,default=0.0)
    pret_cft = models.FloatField(blank=True, null=True,default=0.0)
    pret_rate = models.FloatField(blank=True, null=True,default=0.0)
    pret_days= models.IntegerField(blank=True, null=True,default=0)
    pret_total_cost = models.FloatField(blank=True, null=True,default=0.0)
    pret_created_at = models.DateField(null=True, auto_now_add=True)
    pret_updated_at = models.DateField(null=True, auto_now=True)
    pret_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='pret_updated_by',db_column='pret_updated_by', null=True)
    pret_quantity= models.FloatField(blank=True, null=True,default=0.0)
    pret_size=models.FloatField(blank=True, null=True,default=0.0)
    pret_uom = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE, default='',blank=True, null=True)
    pret_assessment_num=models.ForeignKey(PkneedassessmentInfo, on_delete=models.CASCADE, default='',blank=True, null=True)
    pret_length = models.FloatField(blank=True, null=True, default=0.0)
    pret_stock_type = models.ForeignKey(Pkstocktype, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ["pret_cost_type"]

    def __str__(self):
        return self.pret_cost_type