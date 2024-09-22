from django.db import models
from ..models import Business_Sol_info,MyUser,CustomerInfo

# def sales_directory_path(instance, filename):
#     # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#     return 'Sales_Files/{0}/{1}'.format(instance.s_sale_number, filename)
class BusinessrevenueInfo(models.Model):
    br_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE)
    br_business = models.ForeignKey(Business_Sol_info, on_delete=models.CASCADE)
    br_from_date = models.DateField()
    br_to_date = models.DateField()
    br_sale_person = models.ForeignKey(MyUser, related_name='br_sale_person', db_column='br_sale_person',on_delete=models.CASCADE)
    br_revenue_1 = models.IntegerField(blank=True,null=True)
    br_remarks = models.TextField(max_length=500, default='', blank=True, null=True)
    br_updated_by = models.ForeignKey(MyUser,related_name='br_updated_by', db_column='br_updated_by', on_delete=models.CASCADE)
    br_updated_on = models.DateTimeField(null=True,auto_now=True)
    class Meta:
        ordering = ["br_revenue_1"]

    def __str__(self):
        return self.br_customer_name