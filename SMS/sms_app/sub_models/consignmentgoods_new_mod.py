from django.db import models
from ..models import ConsignmentdetailInfo

class consignmentsgoods_new_info(models.Model):
    cn_consignment_num = models.ForeignKey(ConsignmentdetailInfo, on_delete=models.CASCADE,blank=True,null=True,related_name='cn_consignmentnumber',db_column='cn_consignmentnumber')
    cn_new_goods_pieces = models.FloatField()
    cn_new_goods_length = models.FloatField()
    cn_new_goods_width = models.FloatField()
    cn_new_goods_height = models.FloatField()
    cn_new_goods_weight = models.FloatField()

    class Meta:
        ordering = ["cn_consignment_num"]

    def __str__(self):
        return self.cn_consignment_num