from django.db import models

from .customer_mod import CustomerInfo
from ..models import Location_info, UnitInfo, MyUser,StatusList,approval_status_info,Incident_details_info,CustomerInfo

class IncidentReportInfo(models.Model):
    inc_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, blank=True, null=True)
    inc_unit = models.ForeignKey(UnitInfo, on_delete=models.CASCADE, blank=True, null=True)  # Correct field definition
    inc_incident_date= models.DateTimeField(null=True, blank=True)
    inc_details = models.ForeignKey(Incident_details_info, on_delete=models.CASCADE, blank=False, null=False)
    inc_analysis  = models.CharField(blank=True, null=True, max_length=200)
    inc_action_taken = models.CharField(blank=True, null=True, max_length=200)
    inc_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6, blank=True, null=True)
    inc_CAPA_issueddate = models.DateTimeField(null=True, blank=True)
    inc_CAPA_closeddate = models.DateTimeField(null=True, blank=True)
    inc_approval_status = models.ForeignKey(approval_status_info, on_delete=models.CASCADE, blank=True, null=True)
    inc_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    inc_updated_on = models.DateTimeField(null=True, auto_now=True)
    inc_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True, null=True)