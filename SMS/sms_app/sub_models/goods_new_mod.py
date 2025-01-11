from django.db import models
from ..models import Check_in_out,StatusList

class Warehouse_goods_new_info(models.Model):
    wh_new_job_no = models.CharField(blank=False, null=False, max_length=200, default='')
    wh_new_qr_rand_num = models.CharField(blank=True, null=True, max_length=200)
    wh_new_goods_pieces = models.FloatField()
    wh_new_goods_length = models.FloatField()
    wh_new_goods_width = models.FloatField()
    wh_new_goods_height = models.FloatField()
    wh_new_goods_weight = models.FloatField()
    wh_new_check_in_out= models.CharField(blank=True, null=True, max_length=200)
    wh_new_checkin_time = models.DateTimeField(null=True)
    wh_new_checkout_time = models.DateTimeField(null=True)
    wh_new_goods_status = models.CharField(blank=True, null=True, max_length=200)

    class Meta:
        ordering = ["wh_new_job_no"]

    def __str__(self):
        return self.wh_new_job_no