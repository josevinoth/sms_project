from django.db import models
from ..models import Unitofmeasure,Natypeofreq,Pkstocktype,Stockdescription,PkneedassessmentInfo,MyUser

class Nadimension(models.Model):
    nad_assess_num = models.ForeignKey(PkneedassessmentInfo, on_delete=models.CASCADE, default='')
    nad_length = models.FloatField(default=0.0)
    nad_width = models.FloatField(default=0.0)
    nad_height = models.FloatField(default=0.0)
    nad_quantity = models.IntegerField(default=0)
    nad_created_at = models.DateTimeField(null=True, auto_now_add=True)
    nad_updated_at = models.DateTimeField(null=True, auto_now=True)
    nad_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='nad_updated_by',db_column='nad_updated_by')
    nad_wood_type = models.ForeignKey(Pkstocktype, on_delete=models.CASCADE,limit_choices_to={'id__in': [1, 4]})
    nad_wood_description = models.ForeignKey(Stockdescription, on_delete=models.CASCADE, default='',blank=True,null=True)
    nad_job_weight = models.FloatField( default=0.0)
    nad_type_of_req = models.ForeignKey(Natypeofreq, on_delete=models.CASCADE)
    nad_uom = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE, default='', limit_choices_to={'id__in': [1,2,3,4]},blank=True,null=True)
    nad_plywood_thickness = models.FloatField(default=0.0)
    class Meta:
        ordering = ["nad_assess_num"]

    def __str__(self):
        return self.nad_assess_num