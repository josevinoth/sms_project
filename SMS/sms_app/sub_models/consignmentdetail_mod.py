from django.db import models
from ..models import CustomerInfo,MyUser,MovementtypeInfo,StatusList,YesNoInfo,TrbusinesstypeInfo

class ConsignmentdetailInfo(models.Model):
    co_enquirynumber = models.CharField(max_length=10,default = '')
    co_consignmentnumber = models.CharField(max_length=10,default = '')
    co_consignmentdate = models.DateField(blank=True,null=True)
    co_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE,blank=True,null=True)
    co_consigner = models.CharField(max_length=50,default = '')
    co_consignee = models.CharField(max_length=50,default = '')
    co_consignerinvoice = models.CharField(max_length=50)
    co_consignervalue = models.IntegerField(default='')
    co_valueininr = models.IntegerField(default='')
    co_noofpieces = models.IntegerField(default='')
    co_weight = models.IntegerField(default='')
    co_ebillno = models.CharField(max_length=10,default = '')
    co_dateofissue = models.DateField(blank=True,null=True)
    co_dateofvalidity = models.DateField(blank=True,null=True)
    co_containerdescription = models.CharField(max_length=10,default = '')
    co_dimension = models.CharField(max_length=10,default = '')
    co_movement = models.ForeignKey(MovementtypeInfo,on_delete=models.CASCADE, default='')
    co_status = models.ForeignKey(StatusList,on_delete=models.CASCADE, default='')
    co_lastmodifiedby = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    co_created_at = models.DateTimeField(null=True, auto_now_add=True)
    co_updated_at = models.DateTimeField(null=True, auto_now=True)
    co_cusrefnum = models.CharField(max_length=80)
    co_cusrefnum_check = models.BooleanField(blank=True,null=True)
    co_businesstype = models.ForeignKey(TrbusinesstypeInfo,on_delete=models.CASCADE, blank=True,null=True)


    def __str__(self):
        return self.co_consignmentnumber