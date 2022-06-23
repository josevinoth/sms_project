from django.db import models
from ..models import StatusList

class TripclosureInfo(models.Model):
    tc_enquirynumber = models.CharField(max_length=10,default = '')
    tc_consignmentnumber = models.CharField(max_length=10,default = '')
    tc_tripcost = models.IntegerField(default='')
    tc_parkingcost = models.IntegerField(default='')
    tc_tollcost = models.IntegerField(default='')
    tc_loadingcost = models.IntegerField(default='')
    tc_unloadingcost = models.IntegerField(default='')
    tc_financestatus = models.ForeignKey(StatusList,on_delete=models.CASCADE, default='')
    tc_lastmodifiedby = models.CharField(max_length=30)




    # def __str__(self):
    #     return self.asset_number