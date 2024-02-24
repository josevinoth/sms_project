from django.db import models
from ..models import Business_Sol_info,MyUser,PaymentcycleInfo,GstexcemptionInfo,GstmodelInfo,PaymenttypeInfo,CrcountfromInfo,TrbusinesstypeInfo,CustomertypeInfo

def customercontractinfo_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>

    return 'Customercontractfiles/{0}/{1}'.format(instance.cu_name, filename)
class CustomerInfo(models.Model):
    cu_customercode = models.CharField(max_length=100,default = '')
    cu_name = models.CharField(max_length=100,default = '')
    cu_type= models.ForeignKey(CustomertypeInfo,on_delete=models.CASCADE, default='')
    cu_address =  models.TextField(max_length=500,default = '')
    cu_nameshort = models.CharField(max_length=100,default = '')
    cu_pan = models.CharField(max_length=10,default = '')
    cu_gst =models.CharField(max_length=30,default = '')
    cu_customerperson = models.CharField(max_length=100,default = '')
    cu_designation = models.CharField(max_length=100,default = '')
    cu_contactno = models.CharField(max_length=10,default = '',null=True)
    cu_email = models.EmailField(max_length=50,default = '')
    cu_gstexcepmtion = models.ForeignKey(GstexcemptionInfo,on_delete=models.CASCADE, default='')
    cu_gstmodel = models.ForeignKey(GstmodelInfo,on_delete=models.CASCADE, default='')
    cu_gstpercentage = models.FloatField(default = 0.0)
    cu_paymenttype = models.ForeignKey(PaymenttypeInfo,on_delete=models.CASCADE, default='')
    cu_creditdays = models.IntegerField(default = 0)
    cu_paymentcycle =  models.ForeignKey(PaymentcycleInfo,on_delete=models.CASCADE, default='',null=True)
    cu_creditcountfrom = models.ForeignKey(CrcountfromInfo,on_delete=models.CASCADE, default='')
    cu_tallyid = models.CharField(max_length=100,null=True)
    cu_businessmodel = models.ForeignKey(TrbusinesstypeInfo,on_delete=models.CASCADE, default='')
    cu_lastmodifiedby = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    cu_created_at = models.DateTimeField(null=True, auto_now_add=True)
    cu_updated_at = models.DateTimeField(null=True, auto_now=True)
    cu_business_sol = models.ForeignKey(Business_Sol_info, on_delete=models.CASCADE,blank=True,null=True)
    cu_contract_validity_from = models.DateTimeField(blank=True,null=True)
    cu_contract_validity_to = models.DateTimeField(blank=True,null=True)
    cu_contract = models.FileField(upload_to=customercontractinfo_directory_path, blank=True,null=True)
    class Meta:
        ordering = ["cu_name"]

    def __str__(self):
        return self.cu_name

