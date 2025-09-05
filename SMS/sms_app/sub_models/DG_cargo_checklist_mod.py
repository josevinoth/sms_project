from django.db import models

from .approval_status_mod import approval_status_info
from ..models import Location_info

class DGcargovalueInfo(models.Model):
    DG_wh_job_no = models.CharField(blank=False, null=False, max_length=200, default='')
    DG_wh_location = models.ForeignKey(Location_info, on_delete=models.CASCADE, default='', blank=True,null=True)
    DG_wh_approval_status = models.ForeignKey(approval_status_info, on_delete=models.CASCADE, blank=True, null=True,
                                           default=2)
    DG_wh_first_approval = models.ForeignKey(approval_status_info,on_delete=models.CASCADE,blank=True,null=True,related_name="DG_wh_first_approval")
    DG_wh_second_approval = models.ForeignKey(approval_status_info,on_delete=models.CASCADE,blank=True,null=True,related_name="DG_wh_second_approval")

    def __str__(self):
        return f"DG cargo check at {self.DG_wh_job_no}"