# models.py
from django.db import models

from .driversettlement_expense_mod import Driversettlement_ExpenseInfo
from .tripdetail_mod import TripdetailInfo
from .user_ext_mod import User_extInfo
from ..models import User, ExpenseCategoryInfo, MyUser, Business_Sol_info
from django.urls import reverse

class driver_settlement_info(models.Model):
    staff_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ds_staff_id', to_field='username', db_column='staff_id')
    staff_name = models.CharField(max_length=255)
    transaction_type = models.ForeignKey(ExpenseCategoryInfo, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    business_type = models.ForeignKey(Business_Sol_info, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)
    ds_created_at = models.DateTimeField(null=True, auto_now_add=True)
    ds_updated_at = models.DateTimeField(null=True, auto_now=True)
    ds_updated_by = models.ForeignKey(MyUser, null=True, blank=True, on_delete=models.CASCADE, related_name='ds_updated_by', db_column='ds_updated_by')
    ds_number = models.CharField(max_length=20, null=True, blank=True)
    ds_expense_category = models.ForeignKey(Driversettlement_ExpenseInfo, null=True,blank=True,on_delete=models.CASCADE, default='')
    trip = models.ForeignKey(TripdetailInfo, null=True,on_delete=models.CASCADE, default='')
    total_trip_cost = models.FloatField(default=0.0, blank=True, null=True)
    balance = models.FloatField(default=0.0)  # 👈 new field
    staf_name = models.ForeignKey(User_extInfo, null=True,on_delete=models.CASCADE, default='')

    class Meta:
        ordering = ["ds_number"]

    def __str__(self):
        return self.ds_number or str(self.id)

    def get_absolute_url_ds(self):
        return reverse('driver_settlement_update', args=[str(self.id)])
