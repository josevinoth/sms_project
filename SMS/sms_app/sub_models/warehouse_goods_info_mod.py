from django.db import models
from ..models import Packagetype_info,StatusList,DamageInfo

class Warehouse_goods_info(models.Model):
    UOM_CHOICE = (
        ('cm', 'cm'),
        ('mm', 'mm'),
        ('In', 'In')
    )
    wh_job_no = models.CharField(blank=False, null=False, max_length=20, default='')
    wh_goods_invoice = models.CharField(blank=True, null=True,max_length=20)
    wh_goods_pieces = models.FloatField()
    wh_goods_length = models.FloatField()
    wh_goods_width = models.FloatField()
    wh_goods_height = models.FloatField()
    wh_goods_weight = models.FloatField()
    wh_goods_package_type = models.ForeignKey(Packagetype_info, on_delete=models.CASCADE, default='')
    wh_goods_volume_weight = models.FloatField()
    wh_goods_status = models.ForeignKey(StatusList, on_delete=models.CASCADE,default=6,null=True,related_name='wh_goods_status',db_column='wh_goods_status')
    wh_weights_deviation = models.ForeignKey(StatusList, on_delete=models.CASCADE,null=True,related_name='wh_weights_deviation',db_column='wh_weights_deviation')
    wh_dimension_deviation = models.ForeignKey(StatusList, on_delete=models.CASCADE,null=True,related_name='wh_dimension_deviation',db_column='wh_dimension_deviation')
    wh_no_of_units_deviation = models.ForeignKey(StatusList, on_delete=models.CASCADE,null=True,related_name='wh_no_of_units_deviation',db_column='wh_no_of_units_deviation')
    wh_damages= models.ForeignKey(DamageInfo, on_delete=models.CASCADE, null=True,related_name='wh_damages',db_column='wh_damages')
    wh_mismatches= models.ForeignKey(StatusList, on_delete=models.CASCADE, null=True,related_name='wh_mismatches',db_column='wh_mismatches')
    wh_ratification_process = models.ForeignKey(StatusList, on_delete=models.CASCADE, null=True, related_name='wh_ratification_process',db_column='wh_ratification_process')
    wh_uom = models.CharField(max_length=10, choices=UOM_CHOICE, default='')
    wh_chargeable_weight = models.FloatField()
    wh_CBM = models.FloatField()