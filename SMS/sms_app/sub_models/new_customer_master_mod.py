from django.db import models
from .my_user_mod import MyUser
from .customer_mod import CustomerInfo

class NewCustomerMaster(models.Model):
    customer_name = models.CharField(max_length=200, unique=True, verbose_name="Customer Name")
    is_active = models.BooleanField(default=True, verbose_name="Status (Active/Inactive)")
    is_business_won = models.BooleanField(default=False, verbose_name="Business Won")
    business_won_date = models.DateField(null=True, blank=True, verbose_name="Date of Business Won")
    linked_customer = models.ForeignKey(CustomerInfo, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_customer_origin')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_customers_created')

    class Meta:
        db_table = 'sms_app_newcustomermaster'
        ordering = ['customer_name']
        verbose_name = 'New Customer Master'
        verbose_name_plural = 'New Customer Masters'

    def __str__(self):
        return self.customer_name
