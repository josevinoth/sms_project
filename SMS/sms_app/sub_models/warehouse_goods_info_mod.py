import django
from django.db import models
from django.utils import timezone

from ..models import Fumigation_ActionInfo,Packagetype_info,StatusList,DamageInfo,Location_info,UnitInfo,BayInfo,Check_in_out,GstexcemptionInfo,UOM,StackingInfo

class Warehouse_goods_info(models.Model):
    wh_job_no = models.CharField(blank=False, null=False, max_length=20, default='')
    wh_goods_invoice = models.CharField(blank=True, null=True,max_length=20)
    wh_goods_pieces = models.FloatField(default=0.0)
    wh_goods_length = models.FloatField(default=0.0)
    wh_goods_width = models.FloatField(default=0.0)
    wh_goods_height = models.FloatField(default=0.0)
    wh_goods_weight = models.FloatField(default=0.0)
    wh_goods_package_type = models.ForeignKey(Packagetype_info, on_delete=models.CASCADE, default='')
    wh_goods_volume_weight = models.FloatField(default=0.0)
    wh_goods_status = models.ForeignKey(StatusList, on_delete=models.CASCADE,default=6,null=True,related_name='wh_goods_status',db_column='wh_goods_status')
    wh_weights_deviation = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE,null=True,related_name='wh_weights_deviation',db_column='wh_weights_deviation',default=2)
    wh_dimension_deviation = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE,null=True,related_name='wh_dimension_deviation',db_column='wh_dimension_deviation',default=2)
    wh_no_of_units_deviation = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE,null=True,related_name='wh_no_of_units_deviation',db_column='wh_no_of_units_deviation',default=2)
    wh_damages= models.ForeignKey(DamageInfo, on_delete=models.CASCADE, null=True,related_name='wh_damages',db_column='wh_damages',default=6)
    wh_mismatches= models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, null=True,related_name='wh_mismatches',db_column='wh_mismatches',default=2)
    wh_fumigation_process = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, null=True, blank=True,related_name='wh_fumigation_process',db_column='wh_fumigation_process',default=1)
    wh_fumigation_action = models.ForeignKey(Fumigation_ActionInfo, on_delete=models.CASCADE, null=True)
    wh_fumigation_date=models.DateTimeField(null=True,blank=True)
    wh_uom = models.ForeignKey(UOM, on_delete=models.CASCADE, null=True, related_name='wh_uom',db_column='wh_uom')
    wh_chargeable_weight = models.FloatField(null=True,default=0.0)
    wh_CBM = models.FloatField(null=True,default=0.0)
    wh_branch = models.ForeignKey(Location_info, null=True,on_delete=models.CASCADE, default='')
    wh_unit = models.ForeignKey(UnitInfo,null=True, on_delete=models.CASCADE, default='')
    wh_bay= models.ForeignKey(BayInfo,null=True, on_delete=models.CASCADE, default='')
    wh_available_area = models.FloatField(null=True,default=0.0)
    wh_available_volume = models.FloatField(null=True,default=0.0)
    wh_goods_area = models.FloatField(null=True,default=0.0)
    wh_check_in_out= models.ForeignKey(Check_in_out, on_delete=models.CASCADE, null=True, default=1,related_name='wh_check_in_out',db_column='wh_check_in_out')
    wh_customer_name = models.CharField(blank=True, null=True, max_length=200)
    wh_customer_type = models.CharField(blank=True, null=True, max_length=20)
    wh_stack_layer = models.ForeignKey(StackingInfo, null=True, on_delete=models.CASCADE, default='')
    wh_checkin_time = models.DateTimeField(blank=True, null=True,auto_now=True)
    wh_checkout_time = models.DateTimeField(null=True,blank=True)
    wh_storage_time = models.FloatField(blank=True, null=True,default=0.0)
    wh_qr_rand_num = models.CharField(blank=True, null=True, max_length=20)
    wh_dispatch_num = models.CharField(blank=True, null=True, max_length=20)
    wh_consigner = models.CharField(blank=True, null=True, max_length=20)
    wh_consignee = models.CharField(blank=True, null=True, max_length=20)
    wh_comments = models.TextField(blank=True, null=True)
    wh_invoice_value = models.FloatField(null=True, default=0.0)
    wh_invoice_currency = models.CharField(null=True, max_length=10)
    wh_invoice_amount_inr = models.FloatField(null=True, default=0.0)
    wh_voucher_num = models.CharField(blank=True, null=True, max_length=20)





