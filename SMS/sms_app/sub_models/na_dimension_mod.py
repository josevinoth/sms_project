from django.db import models
from ..models import Naitemname,PkneedassessmentInfo,MyUser

class Nadimension(models.Model):
    nad_assess_num = models.ForeignKey(PkneedassessmentInfo, on_delete=models.CASCADE, default='')
    nad_item_name = models.ForeignKey(Naitemname, on_delete=models.CASCADE, default='')
    nad_length = models.FloatField(blank=True, null=True,default=0.0)
    nad_width = models.FloatField(blank=True, null=True,default=0.0)
    nad_height = models.FloatField(blank=True, null=True,default=0.0)
    nad_quantity = models.IntegerField(blank=True, null=True,default=0)
    nad_created_at = models.DateTimeField(null=True, auto_now_add=True)
    nad_updated_at = models.DateTimeField(null=True, auto_now=True)
    nad_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='nad_updated_by',db_column='nad_updated_by', null=True)

    class Meta:
        ordering = ["nad_assess_num"]

    def __str__(self):
        return self.nad_assess_num