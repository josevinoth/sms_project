from django.db import models
from ..models import CustomerInfo,MyUser,PkneedassessmentInfo

class PkquotationsummaryInfo(models.Model):
    qs_assessment_num = models.OneToOneField(PkneedassessmentInfo, on_delete=models.CASCADE, default='', unique=True)
    qs_wood_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_engineer_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_labour_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_margin = models.FloatField(blank=True, null=True, default=0.0)
    qs_total_cost_wm = models.FloatField(blank=True, null=True, default=0.0)
    qs_rate_per_cft = models.FloatField(blank=True, null=True, default=0.0)
    qs_created_at = models.DateField(null=True, auto_now_add=True)
    qs_updated_at = models.DateField(null=True, auto_now=True)
    qs_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='qs_updated_by',
                                      db_column='qs_updated_by', null=True)
    qs_total_cft = models.FloatField(blank=True, null=True, default=0.0)
    qs_crane_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_ht_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_management_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_material_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_transport_cost = models.FloatField(blank=True, null=True, default=0.0)
    qs_total_cost_wom = models.FloatField(blank=True, null=True, default=0.0)
    qs_address = models.TextField(blank=True, null=True)
    qs_cost_includes = models.TextField(blank=True, null=True)
    qs_notes = models.TextField(blank=True, null=True)
    qs_terms_condition = models.TextField(blank=True, null=True)
    qs_client_scope = models.TextField(blank=True, null=True)
    qs_bvm_scope = models.TextField(blank=True, null=True)
    qs_quotation_number = models.CharField(max_length=100, blank=True, null=True)
    qs_customer_name_2 = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, related_name='qs_customer_name_2',
                                         db_column='qs_customer_name_2', blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return str(self.qs_quotation_number)