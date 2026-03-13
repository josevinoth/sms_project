from django.db import models
from ..models import MyUser
from ..sub_models.vendor_info_mod import Vendor_info
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo


def attached_bill_directory_path(instance, filename):
    return 'attached_bills/{0}/{1}'.format(instance.ab_bill_no, filename)


class AttachedBillInfo(models.Model):
    ab_vendor = models.ForeignKey(Vendor_info, on_delete=models.PROTECT, related_name='ab_vendor_bills', db_column='ab_vendor', null=True, blank=True)
    ab_vehicle_number = models.ForeignKey(VehiclemasterInfo, on_delete=models.PROTECT, related_name='ab_vehicle_bills', db_column='ab_vehicle_number', null=True, blank=True)
    ab_vehicle_type = models.CharField(max_length=100, null=True, blank=True)
    ab_bill_no = models.CharField(max_length=50, null=True, blank=True)
    ab_bill_date = models.DateField(null=True, blank=True)
    ab_from_date = models.DateField(null=True, blank=True)
    ab_to_date = models.DateField(null=True, blank=True)
    ab_buy_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_leave_days = models.IntegerField(default=0)
    ab_trips_not_allotted = models.IntegerField(default=0)
    ab_leave_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_agreed_km = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_total_km_run = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_extra_km_run = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_extra_km_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_bill_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_bill_upload = models.FileField(upload_to=attached_bill_directory_path, null=True, blank=True)
    ab_selected_trips = models.TextField(null=True, blank=True)

    ab_created_at = models.DateTimeField(auto_now_add=True, null=True)
    ab_updated_at = models.DateTimeField(auto_now=True, null=True)
    ab_created_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True, related_name='ab_created_by', db_column='ab_created_by')
    ab_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True, related_name='ab_updated_by', db_column='ab_updated_by')

    class Meta:
        ordering = ['-ab_created_at']

    def __str__(self):
        return f"{self.ab_bill_no} - {self.ab_vehicle_number}"
