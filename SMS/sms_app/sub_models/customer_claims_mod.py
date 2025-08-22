from django.db import models
from ..models import Location_info, UnitInfo, MyUser,StatusList,CustomerInfo,approval_status_info

class CustomerClaimsInfo(models.Model):
    cc_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, blank=True, null=True)
    cc_unit = models.ForeignKey(UnitInfo, on_delete=models.CASCADE, blank=True, null=True)  # Correct field definition)
    cc_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=False, null=False)
    cc_job_ref  = models.CharField(blank=True, null=True, max_length=20)
    cc_supervisor = models.CharField(blank=True, null=True, max_length=200)
    cc_claim_reason = models.CharField(blank=True, null=True, max_length=200)
    cc_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6, blank=True, null=True)
    cc_CAPA_issueddate = models.DateTimeField(null=True, blank=True)
    cc_CAPA_closeddate = models.DateTimeField(null=True, blank=True)
    cc_approval_status = models.ForeignKey(approval_status_info, on_delete=models.CASCADE, blank=True, null=True)
    cc_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    cc_updated_on = models.DateTimeField(null=True, auto_now=True)