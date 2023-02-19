from django.db import models
from ..models import MyUser,StatusList

class TripclosureInfo(models.Model):
    tc_enquirynumber = models.CharField(max_length=10,default = '')
    tc_consignmentnumber = models.CharField(max_length=10,default = '')
    tc_tripnumber = models.CharField(max_length=10, default='')
    tc_tripcost = models.IntegerField(default='')
    tc_parkingcost = models.IntegerField(default='')
    tc_tollcost = models.IntegerField(default='')
    tc_loadingcost = models.IntegerField(default='')
    tc_unloadingcost = models.IntegerField(default='')
    tc_financestatus = models.ForeignKey(StatusList,on_delete=models.CASCADE, default='')
    tc_updated_at = models.DateTimeField(null=True, auto_now=True)
    tc_created_at = models.DateTimeField(null=True, auto_now_add=True)
    tc_updated_by = models.ForeignKey(MyUser, related_name='tc_updated_by', db_column='tc_updated_by',
                                      on_delete=models.CASCADE, null=True)

# def __str__(self):
    #     return self.asset_number