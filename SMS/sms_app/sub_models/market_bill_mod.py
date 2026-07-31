from django.db import models

from .branch_mod import Branch
from ..models import MyUser
from ..sub_models.vendor_info_mod import Vendor_info


class MarketBillInfo(models.Model):
    mb_vendor = models.ForeignKey(Vendor_info,on_delete=models.CASCADE,null=True,blank=True,verbose_name="Vendor")
    mb_vehicle_number = models.CharField(max_length=30,null=True,blank=True,verbose_name="Vehicle Number")
    mb_bill_no = models.CharField(max_length=50,null=True,blank=True,verbose_name="Bill No")
    mb_voucher_no = models.CharField(max_length=100, null=True, blank=True, verbose_name="Voucher No")
    mb_bill_date = models.DateField(null=True,blank=True,verbose_name="Bill Date")
    mb_trip_cost = models.FloatField(default=0.0,null=True,blank=True,verbose_name="Trip Cost")
    mb_loading_cost = models.FloatField(default=0.0,null=True,blank=True,verbose_name="Loading Cost")
    mb_unloading_cost = models.FloatField(default=0.0,null=True,blank=True,verbose_name="Unloading Cost")
    mb_parking_cost = models.FloatField(default=0.0,null=True,blank=True,verbose_name="Parking Cost")
    mb_halting_cost = models.FloatField(default=0.0,null=True,blank=True,verbose_name="Halting Cost")
    mb_halting_days = models.IntegerField(default=0,null=True,blank=True,verbose_name="Halting Days")
    mb_total_cost = models.FloatField(default=0.0,null=True,blank=True,verbose_name="Total Cost")
    # TDS type: Company -> default 2%, Non company -> default 1%
    mb_tds_type = models.CharField(max_length=20, null=True, blank=True, verbose_name="TDS Type",
                                   choices=[('Company', 'Company'), ('Non company', 'Non company')], default='Non company')
    mb_tds_percent = models.FloatField(default=0.0,null=True,blank=True,verbose_name="TDS %")
    mb_tds_amount = models.FloatField(default=0.0,null=True,blank=True,verbose_name="TDS Amount")
    mb_payable_amount = models.FloatField(default=0.0,null=True,blank=True,verbose_name="Payable Amount")
    mb_vehicle_type = models.CharField(max_length=100,null=True,blank=True,verbose_name="Vehicle Type")
    mb_created_at = models.DateTimeField(auto_now_add=True, null=True)
    mb_updated_at = models.DateTimeField(auto_now=True, null=True)
    mb_created_by = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True,blank=True,related_name='market_bill_created_by')
    mb_updated_by = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True,blank=True,related_name='market_bill_updated_by')
    mb_attachment = models.FileField(upload_to='MarketBillAttachments/', null=True, blank=True, verbose_name="Bill Attachment")
    mb_mail_attachment = models.FileField(upload_to='MarketMailAttachments/', null=True, blank=True, verbose_name="Mail Attachment")
    mb_trip_mail_attachments = models.JSONField(default=dict, blank=True, null=True)
    mb_trip_details = models.JSONField(default=dict, blank=True, null=True, verbose_name="Trip Details")
    mb_selected_trips = models.TextField(blank=True, null=True)  # Stores comma-separated trip IDs or JSON

    class Meta:
        ordering = ['-mb_created_at']
        verbose_name = "Market Bill"
        verbose_name_plural = "Market Bills"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.mb_bill_date and self.pk:
            year = self.mb_bill_date.year
            month = self.mb_bill_date.month
            if month >= 4:
                fy_str = f"{str(year)[-2:]}-{str(year+1)[-2:]}"
            else:
                fy_str = f"{str(year-1)[-2:]}-{str(year)[-2:]}"
            month_str_num = f"{month:02d}"
            
            prefix = "MAA"
            if self.mb_selected_trips:
                trip_ids = [tid.strip() for tid in self.mb_selected_trips.split(',') if tid.strip()]
                if trip_ids:
                    from ..sub_models.tripdetail_mod import TripdetailInfo
                    for tid in trip_ids:
                        try:
                            trip = TripdetailInfo.objects.filter(id=int(tid)).first()
                            if trip and trip.tr_consignmentnumber and trip.tr_consignmentnumber.co_consignmentnumber:
                                cnote = trip.tr_consignmentnumber.co_consignmentnumber.upper()
                                if cnote.startswith("BLR"):
                                    prefix = "BLR"
                                    break
                                elif cnote.startswith("MAA"):
                                    prefix = "MAA"
                                    break
                        except ValueError:
                            continue

            # Determine the serial number sequence
            keep_existing = False
            current_serial = None
            if self.mb_voucher_no:
                parts = self.mb_voucher_no.split('_')
                if len(parts) == 5 and parts[0] == prefix and parts[2] == fy_str:
                    keep_existing = True
                    try:
                        current_serial = int(parts[4])
                    except ValueError:
                        pass
            
            if keep_existing and current_serial is not None:
                serial_no = current_serial
            else:
                # Find maximum serial number sequence in existing bills of the same prefix and financial year
                search_prefix = f"{prefix}_MKT_{fy_str}_"
                existing_vouchers = MarketBillInfo.objects.filter(
                    mb_voucher_no__startswith=search_prefix
                ).exclude(pk=self.pk).values_list('mb_voucher_no', flat=True)
                
                max_serial = 0
                for v in existing_vouchers:
                    v_parts = v.split('_')
                    if len(v_parts) == 5:
                        try:
                            ser = int(v_parts[4])
                            if ser > max_serial:
                                max_serial = ser
                        except ValueError:
                            continue
                serial_no = max_serial + 1

            generated_voucher = f"{prefix}_MKT_{fy_str}_{month_str_num}_{serial_no:03d}"
            if self.mb_voucher_no != generated_voucher:
                self.mb_voucher_no = generated_voucher
                super().save(update_fields=['mb_voucher_no'])

    def __str__(self):
        return f"{self.mb_bill_no} - {self.mb_vendor}"
