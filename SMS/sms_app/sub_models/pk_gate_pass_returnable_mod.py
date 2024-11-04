from django.db import models
from ..models import CustomerInfo,PkpurchaseorderInfo,MyUser,Unitofmeasure,Natypeofreq
class PackingGateReturn(models.Model):
    gp_employee = models.CharField(max_length=25)
    gp_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True, null=True)
    gp_sales_order_po = models.ForeignKey(PkpurchaseorderInfo, on_delete=models.CASCADE)
    gp_s_name = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    gp_uom = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE, default='',blank=True, null=True)
    gp_quantity = models.IntegerField(default=0)
    gp_description = models.ForeignKey(Natypeofreq, on_delete=models.CASCADE)

    def __str__(self):
        return f"gate pass at {self.gp_employee}"