from django.db import models
from ..models import MyUser
from ..sub_models.vendor_info_mod import Vendor_info


class MarketBillInfo(models.Model):
    mb_vendor = models.ForeignKey(Vendor_info,on_delete=models.CASCADE,null=True,blank=True,verbose_name="Vendor")
    mb_vehicle_number = models.CharField(max_length=30,null=True,blank=True,verbose_name="Vehicle Number")
    mb_bill_no = models.CharField(max_length=50,null=True,blank=True,verbose_name="Bill No")
    mb_trip_cost = models.FloatField(default=0.0,null=True,blank=True,verbose_name="Trip Cost")
    mb_loading_cost = models.FloatField(default=0.0,null=True,blank=True,verbose_name="Loading Cost")
    mb_unloading_cost = models.FloatField(default=0.0,null=True,blank=True,verbose_name="Unloading Cost")
    mb_parking_cost = models.FloatField(default=0.0,null=True,blank=True,verbose_name="Parking Cost")
    mb_halting_cost = models.FloatField(default=0.0,null=True,blank=True,verbose_name="Halting Cost")
    mb_halting_days = models.IntegerField(default=0,null=True,blank=True,verbose_name="Halting Days")
    mb_total_cost = models.FloatField(default=0.0,null=True,blank=True,verbose_name="Total Cost")
    mb_vehicle_type = models.CharField(max_length=100,null=True,blank=True,verbose_name="Vehicle Type")
    mb_selected_trips = models.TextField(null=True,blank=True,verbose_name="Selected Trip IDs")
    mb_created_at = models.DateTimeField(auto_now_add=True, null=True)
    mb_updated_at = models.DateTimeField(auto_now=True, null=True)
    mb_created_by = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True,blank=True,related_name='market_bill_created_by')
    mb_updated_by = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True,blank=True,related_name='market_bill_updated_by')
    mb_attachment = models.FileField(upload_to='MarketBillAttachments/', null=True, blank=True, verbose_name="Bill Attachment")
    mb_mail_attachment = models.FileField(upload_to='MarketMailAttachments/', null=True, blank=True, verbose_name="Mail Attachment")

    class Meta:
        ordering = ['-mb_created_at']
        verbose_name = "Market Bill"
        verbose_name_plural = "Market Bills"

    def __str__(self):
        return f"{self.mb_bill_no} - {self.mb_vendor}"
