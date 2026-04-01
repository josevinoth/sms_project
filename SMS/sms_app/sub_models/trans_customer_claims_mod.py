from django.db import models

class TransCustomerClaimsInfo(models.Model):
    tcc_cnote = models.ForeignKey('ConsignmentdetailInfo', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Cnote No")
    tcc_customer_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Customer Name")
    tcc_trip_date = models.DateField(null=True, blank=True, verbose_name="Trip Date")
    tcc_from = models.CharField(max_length=200, blank=True, null=True, verbose_name="From")
    tcc_to = models.CharField(max_length=200, blank=True, null=True, verbose_name="To")
    tcc_veh_no = models.CharField(max_length=20, blank=True, null=True, verbose_name="Veh No")
    tcc_veh_type = models.CharField(max_length=150, blank=True, null=True, verbose_name="Veh Type")
    tcc_driver_no = models.CharField(max_length=30, blank=True, null=True, verbose_name="Driver No")
    tcc_driver_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Driver Name")
    tcc_shipper_ref_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="Shipper Reference No")
    tcc_total_pkg = models.IntegerField(default=0, blank=True, null=True, verbose_name="Total No.of pkg")
    tcc_damaged_pkg = models.IntegerField(default=0, blank=True, null=True, verbose_name="No.of Pkg Damaged")
    tcc_damage_remarks = models.CharField(max_length=500, blank=True, null=True, verbose_name="Damage remarks")
    tcc_reason_for_claim = models.CharField(max_length=200, blank=True, null=True, verbose_name="Reason for Claim")
    tcc_claim_amount = models.FloatField(default=0.0, blank=True, null=True, verbose_name="Claim Amount")
    tcc_capa_issued_date = models.DateField(null=True, blank=True, verbose_name="CAPA issued date")
    tcc_capa_closed_date = models.DateField(null=True, blank=True, verbose_name="CAPA clsoed date")
    tcc_mgmt_approval = models.ForeignKey('approval_status_info', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Management Approval")
    tcc_current_status = models.ForeignKey('StatusList', on_delete=models.CASCADE, default=6, blank=True, null=True, verbose_name="Current Status")
    tcc_updated_by = models.ForeignKey('MyUser', on_delete=models.CASCADE, null=True, blank=True)
    tcc_updated_on = models.DateTimeField(null=True, auto_now=True)
    
    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return str(self.tcc_cnote)
