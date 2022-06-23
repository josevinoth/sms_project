from django.db import models
from ..models import MovementtypeInfo,StatusList

class ConsignmentdetailInfo(models.Model):
    co_enquirynumber = models.CharField(max_length=10,default = '')
    co_consignmentnumber = models.CharField(max_length=10,default = '')
    co_consignmentdate = models.CharField(max_length=10,default = '')
    co_consigner = models.CharField(max_length=10,default = '')
    co_consignee = models.CharField(max_length=10,default = '')
    co_consignerinvoice = models.CharField(max_length=30)
    co_consignervalue = models.IntegerField(default='')
    co_valueininr = models.IntegerField(default='')
    co_noofpieces = models.IntegerField(default='')
    co_weight = models.IntegerField(default='')
    co_ebillno = models.CharField(max_length=10,default = '')
    co_dateofissue = models.CharField(max_length=10,default = '')
    co_dateofvalidity = models.CharField(max_length=10,default = '')
    co_containerdescription = models.CharField(max_length=10,default = '')
    co_dimension = models.CharField(max_length=10,default = '')
    co_movement = models.ForeignKey(MovementtypeInfo,on_delete=models.CASCADE, default='')
    co_status = models.ForeignKey(StatusList,on_delete=models.CASCADE, default='')
    co_lastmodifiedby = models.CharField(max_length=30)



    def __str__(self):
        return self.co_consignmentnumber