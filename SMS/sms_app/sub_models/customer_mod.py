from django.db import models
from ..models import State,StatusList,GstmodelInfo,PaymenttypeInfo,CrcountfromInfo,CustomerdepartmentInfo,TrbusinesstypeInfo

class CustomerInfo(models.Model):
    cu_customercode = models.CharField(max_length=10,default = '')
    cu_name = models.CharField(max_length=10,default = '')
    cu_state = models.ForeignKey(State,on_delete=models.CASCADE, default='')
    cu_nameshort = models.CharField(max_length=10,default = '')
    cu_pan = models.CharField(max_length=10,default = '')
    cu_gst = models.CharField(max_length=30)
    cu_customerperson = models.IntegerField(default='')
    cu_designation = models.IntegerField(default='')
    cu_contactno = models.IntegerField(default='')
    cu_email = models.IntegerField(default='')
    cu_gstexcepmtion = models.ForeignKey(StatusList,on_delete=models.CASCADE, default='')
    cu_gstmodel = models.ForeignKey(GstmodelInfo,on_delete=models.CASCADE, default='')
    cu_gstpercentage = models.CharField(max_length=10,default = '')
    cu_paymenttype = models.ForeignKey(PaymenttypeInfo,on_delete=models.CASCADE, default='')
    cu_creditdays = models.CharField(max_length=10,default = '')
    cu_paymentcycle = models.CharField(max_length=30)
    cu_creditcountfrom = models.ForeignKey(CrcountfromInfo,on_delete=models.CASCADE, default='')
    cu_department = models.ForeignKey(CustomerdepartmentInfo,on_delete=models.CASCADE, default='')
    cu_tallyid = models.CharField(max_length=30)
    cu_businessmodel = models.ForeignKey(TrbusinesstypeInfo,on_delete=models.CASCADE, default='')
    cu_lastmodifiedby = models.CharField(max_length=30)

    def __str__(self):
        return self.cu_name