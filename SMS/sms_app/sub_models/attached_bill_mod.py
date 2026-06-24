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
    ab_bill_no = models.CharField(max_length=50)
    ab_voucher_no = models.CharField(max_length=100, null=True, blank=True, verbose_name="Voucher No")
    ab_bill_date = models.DateField(null=True, blank=True)
    ab_from_date = models.DateField(null=True, blank=True)
    ab_to_date = models.DateField(null=True, blank=True)
    ab_buy_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_leave_days = models.IntegerField(default=0)
    ab_trips_not_allotted = models.IntegerField(default=0)
    ab_leave_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_toll_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_agreed_km = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_total_km_run = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_extra_km_run = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_extra_km_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ab_bill_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    # TDS type and fields (match MarketBill behaviour)
    ab_tds_type = models.CharField(max_length=20, null=True, blank=True, verbose_name="TDS Type",
                                   choices=[('Company', 'Company'), ('Non company', 'Non company')], default='Non company')
    ab_tds_percent = models.FloatField(default=0.0, null=True, blank=True)
    ab_tds_amount = models.FloatField(default=0.0, null=True, blank=True)
    ab_payable_amount = models.FloatField(default=0.0, null=True, blank=True)
    ab_bill_upload = models.FileField(upload_to=attached_bill_directory_path, null=True, blank=True)
    ab_selected_trips = models.TextField(null=True, blank=True)

    ab_created_at = models.DateTimeField(auto_now_add=True, null=True)
    ab_updated_at = models.DateTimeField(auto_now=True, null=True)
    ab_created_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True, related_name='ab_created_by', db_column='ab_created_by')
    ab_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True, related_name='ab_updated_by', db_column='ab_updated_by')

    @property
    def ab_total_buy_cost(self):
        """Bill Amount - Extra KM Amount - Toll Cost"""
        return (self.ab_bill_amount or 0) - (self.ab_extra_km_amount or 0) - (self.ab_toll_cost or 0)


    class Meta:
        ordering = ['-ab_created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.ab_bill_date and self.pk:
            year = self.ab_bill_date.year
            month = self.ab_bill_date.month
            if month >= 4:
                fy_str = f"{str(year)[-2:]}-{str(year+1)[-2:]}"
            else:
                fy_str = f"{str(year-1)[-2:]}-{str(year)[-2:]}"
            month_str_num = f"{month:02d}"

            prefix = "MAA"
            if self.ab_selected_trips:
                trip_numbers = [t.strip() for t in self.ab_selected_trips.split(',') if t.strip()]
                if trip_numbers:
                    from ..sub_models.tripdetail_mod import TripdetailInfo
                    trips = TripdetailInfo.objects.filter(tr_tripnumber__in=trip_numbers)
                    for trip in trips:
                        if trip.tr_consignmentnumber and trip.tr_consignmentnumber.co_consignmentnumber:
                            cnote = trip.tr_consignmentnumber.co_consignmentnumber.upper()
                            if cnote.startswith("BLR"):
                                prefix = "BLR"
                                break
                            elif cnote.startswith("MAA"):
                                prefix = "MAA"
                                break

            # Determine the serial number sequence
            keep_existing = False
            current_serial = None
            if self.ab_voucher_no:
                parts = self.ab_voucher_no.split('_')
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
                search_prefix = f"{prefix}_ATT_{fy_str}_"
                existing_vouchers = AttachedBillInfo.objects.filter(
                    ab_voucher_no__startswith=search_prefix
                ).exclude(pk=self.pk).values_list('ab_voucher_no', flat=True)

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

            generated_voucher = f"{prefix}_ATT_{fy_str}_{month_str_num}_{serial_no:03d}"
            if self.ab_voucher_no != generated_voucher:
                self.ab_voucher_no = generated_voucher
                super().save(update_fields=['ab_voucher_no'])

    def __str__(self):
        return f"{self.ab_bill_no} - {self.ab_vehicle_number}"
