from django.db import models
from django.contrib.auth.models import User
from ..sub_models.customer_mod import CustomerInfo
from ..sub_models.customerdepartment_mod import CustomerdepartmentInfo
from ..sub_models.places_mod import Places

class DmrInfo(models.Model):
    dmr_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE)
    dmr_department = models.ForeignKey(CustomerdepartmentInfo, on_delete=models.SET_NULL, null=True, blank=True)
    dmr_month = models.IntegerField(null=True, blank=True)
    dmr_year = models.IntegerField(null=True, blank=True)
    dmr_from_location = models.ForeignKey(Places, on_delete=models.SET_NULL, null=True, blank=True, related_name='dmr_from_set')
    dmr_to_location = models.ForeignKey(Places, on_delete=models.SET_NULL, null=True, blank=True, related_name='dmr_to_set')
    dmr_recipient = models.TextField(blank=True, null=True)
    dmr_cc = models.TextField(blank=True, null=True)
    dmr_subject = models.CharField(max_length=255, blank=True, null=True)
    dmr_trip_count = models.IntegerField(default=0)
    dmr_sent_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    dmr_sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"DMR sent for {self.dmr_customer} on {self.dmr_sent_at}"
