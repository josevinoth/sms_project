from django.db import models
from ..models import MyUser

class Sales_target_info(models.Model):
    st_start_date = models.DateField(null=True,blank=True)
    st_end_date = models.DateField(null=True,blank=True)
    st_target_revenue = models.FloatField(null=True,blank=True,default=0.0)
    st_target_customer = models.IntegerField(null=True,blank=True,default=0)
    st_sales_person = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name='st_sales_person', db_column='st_sales_person')
    st_created_at = models.DateTimeField(null=True, auto_now_add=True)
    st_updated_at = models.DateTimeField(null=True, auto_now=True)
    st_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    st_remarks = models.TextField(null=False, blank=True)
    st_target_calls_new_customer = models.FloatField(null=True, blank=True, default=0.0)
    st_target_calls_existing_customer = models.FloatField(null=True, blank=True, default=0.0)
    st_target_calls_review = models.FloatField(null=True, blank=True, default=0.0)
    st_company = models.ForeignKey('Business_Sol_info', null=True, blank=True, on_delete=models.SET_NULL, related_name='st_company')
    st_target_calls = models.IntegerField(null=True, blank=True, default=0)
    st_target_revenue_existing = models.FloatField(null=True, blank=True, default=0.0)
    st_target_revenue_new = models.FloatField(null=True, blank=True, default=0.0)
    st_target_customers_new = models.IntegerField(null=True, blank=True, default=0)
    st_target_customers_existing = models.IntegerField(null=True, blank=True, default=0)
    st_target_customers_onboard = models.IntegerField(null=True, blank=True, default=0)
