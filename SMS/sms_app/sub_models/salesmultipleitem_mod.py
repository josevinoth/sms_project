from django.db import models
from ..models import YesNoInfo,CustomerInfo

class SalesmultipleitemInfo(models.Model):
    sm_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True,null=True)
    sm_Date_of_Quote = models.DateField()
    sm_Quote_Ref = models.CharField(max_length=100,null=True,blank=True)
    sm_Rate_Approval = models.ForeignKey(YesNoInfo,on_delete=models.CASCADE,default='')

    class Meta:
        ordering = ["sm_Date_of_Quote"]

    def __str__(self):
        return str(self.sm_Date_of_Quote)