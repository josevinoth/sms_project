from django.db import models
from ..models import MyUser
from .vendorratemaster1_mod import VendorratemasterInfo1

class VendorratemasterHistory(models.Model):
    rate_master = models.ForeignKey(VendorratemasterInfo1, on_delete=models.CASCADE, related_name='history_logs')
    old_rate = models.IntegerField(null=True, blank=True)
    new_rate = models.IntegerField(null=True, blank=True)
    
    old_agreement_type = models.ForeignKey('sms_app.AgreementType', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    new_agreement_type = models.ForeignKey('sms_app.AgreementType', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    old_validity_from = models.DateField(null=True, blank=True)
    new_validity_from = models.DateField(null=True, blank=True)
    old_validity_to = models.DateField(null=True, blank=True)
    new_validity_to = models.DateField(null=True, blank=True)
    
    action_type = models.CharField(max_length=50, default='UPDATE')
    changed_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-changed_at']
        db_table = 'sms_app_vendorratemasterhistory'
