from django.db import models
from ..models import ConsignmentdetailInfo,MyUser

class consignmentsgoods_new_info(models.Model):
    cn_consignment_num = models.ForeignKey(ConsignmentdetailInfo, on_delete=models.CASCADE,blank=True,null=True,related_name='cn_consignmentnumber',db_column='cn_consignmentnumber')
    cn_new_goods_pieces = models.FloatField()
    cn_new_goods_length = models.FloatField()
    cn_new_goods_width = models.FloatField()
    cn_new_goods_height = models.FloatField()
    cn_new_goods_weight = models.FloatField()
    cn_lastmodifiedby = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True)
    cn_created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    cn_updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        ordering = ["cn_consignment_num"]

    def __str__(self):
        return self.cn_consignment_num