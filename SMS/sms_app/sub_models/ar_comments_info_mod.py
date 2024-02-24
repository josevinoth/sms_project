from django.db import models
from ..models import MyUser,CustomerInfo

class Ar_comments_Info(models.Model):
    arc_invoice_num = models.CharField(max_length=30,null=True, blank=True)
    arc_comments = models.TextField(max_length=500)
    arc_created_at = models.DateTimeField(null=True, auto_now_add=True)
    arc_updated_at = models.DateTimeField(null=True, auto_now=True)
    arc_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name='arc_updated_by', db_column='arc_updated_by', null=True)
    arc_customer = models.ForeignKey(CustomerInfo,on_delete=models.CASCADE,related_name='arc_customer', db_column='arc_customer')
    arc_customer_contact_name = models.CharField(max_length=100, null=True, blank=True)
    arc_customer_contact_designation = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        ordering = ["arc_invoice_num"]

    def __str__(self):
        return self.arc_comments