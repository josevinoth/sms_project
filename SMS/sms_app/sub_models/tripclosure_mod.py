from django.db import models
from ..models import ConsignmentdetailInfo,MyUser,Tripstatusinfo

class TripclosureInfo(models.Model):
    tc_enquirynumber = models.CharField(max_length=10,default = '')
    tc_consignmentnumber = models.ForeignKey(ConsignmentdetailInfo, on_delete=models.CASCADE)
    tc_tripnumber = models.CharField(max_length=10, default='')
    tc_tripcost = models.FloatField(default=0.0)
    tc_parkingcost = models.FloatField(default=0.0)
    tc_tollcost = models.FloatField(default=0.0)
    tc_loadingcost = models.FloatField(default=0.0)
    tc_unloadingcost = models.FloatField(default=0.0)
    tc_weighmentcost = models.FloatField(default=0.0)
    tc_handlingcost = models.FloatField(default=0.0)
    tc_financestatus = models.ForeignKey(Tripstatusinfo,on_delete=models.CASCADE, default='')
    tc_updated_at = models.DateTimeField(null=True, auto_now=True)
    tc_created_at = models.DateTimeField(null=True, auto_now_add=True)
    tc_updated_by = models.ForeignKey(MyUser, related_name='tc_updated_by', db_column='tc_updated_by',on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ["tc_financestatus"]
    def __str__(self):
        return self.tc_financestatus
