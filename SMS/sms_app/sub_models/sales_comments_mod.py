from django.db import models
from ..models import SalesInfo,Callpurpose,Callnature,Calltype,MyUser

class Sales_Comments_Info(models.Model):
    sc_sales_number = models.ForeignKey(SalesInfo, related_name='SalesInfo', db_column='SalesInfo',on_delete=models.CASCADE, null=True,)
    sc_call_type = models.ForeignKey(Calltype,on_delete=models.CASCADE, default='')
    sc_call_nature = models.ForeignKey(Callnature,on_delete=models.CASCADE, default='')
    sc_call_purpose = models.ForeignKey(Callpurpose,on_delete=models.CASCADE, default='')
    sc_updated_by = models.ForeignKey(MyUser, related_name='sc_added_by', db_column='sc_added_by',on_delete=models.CASCADE, null=True,)
    sc_created_at = models.DateTimeField(null=True, auto_now_add=True)
    sc_updated_at = models.DateTimeField(null=True, auto_now=True)
    sc_comments = models.TextField(max_length=300,null=True, blank=True)
    sc_complaints = models.TextField(max_length=300,null=True, blank=True)
    sc_compliments = models.TextField(max_length=300,null=True, blank=True)
    sc_date_of_call = models.DateField()

    class Meta:
        ordering = ["sc_sales_number"]

    def __str__(self):
        return self.sc_sales_number