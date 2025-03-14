from django.db import models
from ..models import MyUser,YesNoInfo,SalesInfo

def sales_multiple_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'sales_multiple_files/{0}/{1}'.format(instance.sm_sales_num, filename)
class SalesmultipleitemInfo(models.Model):
    sm_sales_num = models.ForeignKey(SalesInfo, on_delete=models.CASCADE, blank=True,null=True)
    sm_Date_of_Quote = models.DateField()
    sm_Quote_Ref = models.CharField(max_length=100)
    sm_Rate_Approval = models.ForeignKey(YesNoInfo,on_delete=models.CASCADE,default='')
    sm_lastmodifiedby = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    sm_updated_at = models.DateTimeField(null=True, auto_now=True)
    sm_attachment = models.FileField(upload_to=sales_multiple_path, null=True, blank=True)

    class Meta:
        ordering = ["sm_sales_num"]

    def __str__(self):
        return str(self.sm_sales_num)