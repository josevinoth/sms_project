from django.db import models
from .pk_costing_mod import PkcostingInfo
from django.contrib.auth.models import User
from .my_user_mod import MyUser

class PkProductionReturn(models.Model):
    pr_job_no = models.CharField(max_length=100, null=True, blank=True)
    pr_costing_item = models.ForeignKey(PkcostingInfo, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Return details
    pr_return_qty = models.FloatField(default=0.0)
    pr_return_l = models.FloatField(default=0.0, null=True, blank=True)
    pr_return_w = models.FloatField(default=0.0, null=True, blank=True)
    pr_return_h = models.FloatField(default=0.0, null=True, blank=True)
    pr_orig_l = models.FloatField(default=0.0, null=True, blank=True)
    pr_orig_w = models.FloatField(default=0.0, null=True, blank=True)
    pr_orig_h = models.FloatField(default=0.0, null=True, blank=True)
    
    # Cost details
    pr_rate = models.FloatField(default=0.0)
    pr_fraction = models.FloatField(default=1.0)
    pr_cost_to_reduce = models.FloatField(default=0.0)
    
    # Classification
    pr_return_type = models.CharField(max_length=50, default='Good') # 'Good' or 'Damaged'
    pr_status = models.CharField(max_length=50, default='Pending') # 'Pending' or 'Accepted'
    
    # Auditing
    pr_created_by = models.ForeignKey(MyUser, related_name='production_return_created', on_delete=models.SET_NULL, null=True)
    pr_created_at = models.DateTimeField(auto_now_add=True)
    pr_accepted_at = models.DateTimeField(null=True, blank=True)
    pr_accepted_by = models.ForeignKey(MyUser, related_name='production_return_accepted', on_delete=models.SET_NULL, null=True, blank=True)
    pr_grn_number = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.pr_job_no} - {self.pr_return_qty} - {self.pr_status}"
