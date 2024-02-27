from django.db import models
from ..models import MyUser,PkneedassessmentInfo

class PkquotationsummaryInfo(models.Model):
    qs_assessment_num=models.OneToOneField(PkneedassessmentInfo, on_delete=models.CASCADE, default='',unique=True)
    qs_wood_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_engineer_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_labour_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_margin = models.FloatField(blank=True, null=True, default=0.0)
    qs_total_cost_wm = models.FloatField(blank=True, null=True, default=0.0)
    qs_rate_per_cft = models.FloatField(blank=True, null=True, default=0.0)
    qs_created_at = models.DateField(null=True, auto_now_add=True)
    qs_updated_at = models.DateField(null=True, auto_now=True)
    qs_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='qs_updated_by',db_column='qs_updated_by', null=True)
    qs_total_cft = models.FloatField(blank=True, null=True, default=0.0)
    qs_crane_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_ht_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_management_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_material_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_transport_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_total_cost_wom = models.FloatField(blank=True, null=True, default=0.0)
    qs_remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["qs_wood_cost"]

    def __str__(self):
        return self.qs_assessment_num