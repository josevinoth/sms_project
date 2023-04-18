from django.db import models
from ..models import Callpurpose,Callnature,Calltype,MyUser

class Sales_Comments_Info(models.Model):
    sc_sales_number = models.CharField(max_length=30,default = '')
    sc_call_type = models.ForeignKey(Calltype, blank=True, null=True, on_delete=models.CASCADE, default='')
    sc_call_nature = models.ForeignKey(Callnature, blank=True, null=True, on_delete=models.CASCADE, default='')
    sc_call_purpose = models.ForeignKey(Callpurpose, blank=True, null=True, on_delete=models.CASCADE, default='')
    sc_updated_by = models.ForeignKey(MyUser, related_name='sc_added_by', db_column='sc_added_by',on_delete=models.CASCADE, null=True,)
    sc_created_at = models.DateTimeField(null=True, auto_now_add=True)
    sc_updated_at = models.DateTimeField(null=True, auto_now=True)
    sc_comments = models.TextField(null=True, blank=True)
    sc_complaints = models.TextField(null=True, blank=True)
    sc_compliments = models.TextField(null=True, blank=True)
    sc_date_of_call = models.DateField()

    class Meta:
        ordering = ["sc_sales_number"]

    def __str__(self):
        return self.sc_sales_number