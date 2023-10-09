from django.db import models
from ..models import EnquirynoteInfo,Currency_type,CustomerInfo,MyUser,GST_payable_info,StatusList

class ConsignmentdetailInfo(models.Model):
    co_enquirynumber = models.ForeignKey(EnquirynoteInfo, on_delete=models.CASCADE,blank=True,null=True)
    co_consignmentnumber = models.CharField(max_length=20,blank=True,null=True)
    co_consignmentdate = models.DateField(blank=True,null=True)
    co_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE,blank=True,null=True)
    co_containerdescription = models.CharField(max_length=10,default = '',null=True,blank=True)
    co_freight_amount = models.CharField(max_length=100,default = 'As Agreed',null=True,blank=True)
    co_seal_number = models.CharField(max_length=100,default ='',null=True,blank=True)
    co_container_number = models.CharField(max_length=100,default ='',null=True,blank=True)
    co_status = models.ForeignKey(StatusList,on_delete=models.CASCADE, default='')
    co_gst_payable_by = models.ForeignKey(GST_payable_info, on_delete=models.CASCADE, null=True,blank=True)
    co_lastmodifiedby = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True,blank=True)
    co_created_at = models.DateTimeField(null=True,blank=True, auto_now_add=True)
    co_updated_at = models.DateTimeField(null=True,blank=True, auto_now=True)
    co_cusrefnum = models.CharField(max_length=80,null=True,blank=True)
    co_cusrefnum_check = models.BooleanField(blank=True,null=True)

    def __str__(self):
        return self.co_consignmentnumber