from datetime import timezone

from django.db import models
from django.contrib.auth.models import User
from ..models import Dispatch_info,Warehouse_goods_info


class GoodsPartialDispatchInfo(models.Model):
    pd_goods = models.ForeignKey(Warehouse_goods_info, on_delete=models.CASCADE)
    pd_dispatch_qty = models.FloatField()
    pd_dispatch_time = models.DateTimeField(null=True, blank=True)
    pd_dispatch_info = models.ForeignKey(Dispatch_info, on_delete=models.CASCADE)
    pd_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
