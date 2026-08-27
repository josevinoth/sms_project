from django.db import models
from ..models import MyUser, CustomerInfo, CustomerdepartmentInfo, VehicletypeInfo, VehiclecategoryInfo, Places
from .rtratemaster_mod import RtratemasterInfo

class RtratemasterHistory(models.Model):
    rate_master = models.ForeignKey(RtratemasterInfo, on_delete=models.CASCADE, related_name='history_logs')
    old_rate = models.IntegerField(null=True, blank=True)
    new_rate = models.IntegerField(null=True, blank=True)
    action_type = models.CharField(max_length=50, default='UPDATE') # CREATE, UPDATE, DELETE
    changed_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"Rate History #{self.id} for Master #{self.rate_master_id}"
