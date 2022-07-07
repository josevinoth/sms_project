from django.db import models
from ..models import Packagetype_info

class Warehouse_goods_info(models.Model):
    wh_job_no = models.CharField(blank=False, null=False, max_length=20, default='')
    wh_goods_invoice = models.CharField(blank=True, null=True,max_length=20)
    wh_goods_pieces = models.IntegerField()
    wh_goods_length = models.IntegerField()
    wh_goods_width = models.IntegerField()
    wh_goods_height = models.IntegerField()
    wh_goods_weight = models.IntegerField()
    wh_goods_package_type = models.ForeignKey(Packagetype_info, on_delete=models.CASCADE, default='')
    wh_goods_volume_weight = models.IntegerField()