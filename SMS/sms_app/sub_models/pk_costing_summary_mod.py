from django.db import models
from ..models import pk_itemdescriptionInfo,pk_itemInfo,MyUser,PkneedassessmentInfo

class PkcostingsummaryInfo(models.Model):
    cs_assessment_num=models.OneToOneField(PkneedassessmentInfo, on_delete=models.CASCADE, default='',unique=True)
    cs_wood_cost = models.FloatField(blank=True, null=True, default=0.0)
    cs_engineer_cost = models.FloatField(blank=True, null=True, default=0.0)
    cs_labour_cost = models.FloatField(blank=True, null=True, default=0.0)
    cs_margin = models.FloatField(blank=True, null=True, default=0.0)
    cs_total_cost_wm = models.FloatField(blank=True, null=True, default=0.0)
    cs_rate_per_cft = models.FloatField(blank=True, null=True, default=0.0)
    cs_created_at = models.DateField(null=True, auto_now_add=True)
    cs_updated_at = models.DateField(null=True, auto_now=True)
    cs_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='cs_updated_by',db_column='cs_updated_by', null=True)
    cs_total_cft = models.FloatField(blank=True, null=True, default=0.0)
    cs_crane_cost = models.FloatField(blank=True, null=True, default=0.0)
    cs_ht_cost = models.FloatField(blank=True, null=True, default=0.0)
    cs_management_cost = models.FloatField(blank=True, null=True, default=0.0)
    cs_material_cost = models.FloatField(blank=True, null=True, default=0.0)
    cs_transport_cost = models.FloatField(blank=True, null=True, default=0.0)
    cs_total_cost_wom = models.FloatField(blank=True, null=True, default=0.0)
    cs_remarks = models.TextField(blank=True, null=True)
    cs_address = models.TextField(blank=True, null=True)
    cs_cost_includes = models.TextField(blank=True, null=True)
    cs_notes = models.TextField(blank=True, null=True)
    cs_terms_condition = models.TextField(blank=True, null=True)
    cs_client_scope = models.TextField(blank=True, null=True)
    cs_bvm_scope = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.cs_total_cost_wm