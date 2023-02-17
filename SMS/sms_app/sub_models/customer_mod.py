from django.db import models
from ..models import MyUser,PaymentcycleInfo,GstexcemptionInfo,GstmodelInfo,PaymenttypeInfo,CrcountfromInfo,TrbusinesstypeInfo,CustomertypeInfo


class CustomerInfo(models.Model):
    cu_customercode = models.CharField(max_length=100,default = '')
    cu_name = models.CharField(max_length=100,default = '')
    cu_type= models.ForeignKey(CustomertypeInfo,on_delete=models.CASCADE, default='')
    cu_address =  models.CharField(max_length=200,default = '')
    cu_nameshort = models.CharField(max_length=100,default = '')
    cu_pan = models.CharField(max_length=10,default = '')
    cu_gst =models.CharField(max_length=30,default = '')
    cu_customerperson = models.CharField(max_length=30,default = '')
    cu_designation = models.CharField(max_length=10,default = '')
    cu_contactno = models.CharField(max_length=10,default = '',null=True)
    cu_email = models.EmailField(max_length=50,default = '')
    cu_gstexcepmtion = models.ForeignKey(GstexcemptionInfo,on_delete=models.CASCADE, default='')
    cu_gstmodel = models.ForeignKey(GstmodelInfo,on_delete=models.CASCADE, default='')
    cu_gstpercentage = models.CharField(max_length=10,default = '')
    cu_paymenttype = models.ForeignKey(PaymenttypeInfo,on_delete=models.CASCADE, default='')
    cu_creditdays = models.CharField(max_length=10,default = '')
    cu_paymentcycle =  models.ForeignKey(PaymentcycleInfo,on_delete=models.CASCADE, default='',null=True)
    cu_creditcountfrom = models.ForeignKey(CrcountfromInfo,on_delete=models.CASCADE, default='')
    cu_tallyid = models.CharField(max_length=30,null=True)
    cu_businessmodel = models.ForeignKey(TrbusinesstypeInfo,on_delete=models.CASCADE, default='')
    cu_lastmodifiedby = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    cu_created_at = models.DateTimeField(null=True, auto_now_add=True)
    cu_updated_at = models.DateTimeField(null=True, auto_now=True)

    class Meta:
        ordering = ["cu_name"]

    def __str__(self):
        return self.cu_name