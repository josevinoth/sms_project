from django.db import models
from ..models import MyUser,PkneedassessmentInfo

class PkcostingsummaryInfo(models.Model):
    cs_assessment_num=models.ForeignKey(PkneedassessmentInfo, on_delete=models.CASCADE, default='')
    cs_wood_cost = models.FloatField(blank=True, null=True, default=0.0)
    cs_engineer_cost = models.FloatField(blank=True, null=True, default=0.0)
    cs_labour_cost = models.FloatField(blank=True, null=True, default=0.0)
    cs_total_cost_wom = models.FloatField(blank=True, null=True, default=0.0)
    cs_margin = models.FloatField(blank=True, null=True, default=0.0)
    cs_total_cost_wm = models.FloatField(blank=True, null=True, default=0.0)
    cs_rate_per_cft = models.FloatField(blank=True, null=True, default=0.0)
    cs_created_at = models.DateField(null=True, auto_now_add=True)
    cs_updated_at = models.DateField(null=True, auto_now=True)
    cs_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='cs_updated_by',db_column='cs_updated_by', null=True)

    class Meta:
        ordering = ["cs_wood_cost"]

    def __str__(self):
        return self.cs_wood_cost