from django.db import models
from ..models import approval_status_info,MyUser

class Trip_approval_info(models.Model):
    ta_approval_status = models.ForeignKey(approval_status_info, on_delete=models.CASCADE, blank=True, null=True)
    ta_approved_on = models.DateTimeField(null=True, blank=True, auto_now=True)
    ta_approved_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ["ta_approval_status"]

    def __str__(self):
        return str(self.ta_approval_status) if self.ta_approval_status else f"Approval #{self.id}"
