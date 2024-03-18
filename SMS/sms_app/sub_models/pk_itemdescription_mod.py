from django.db import models
from ..models import pk_itemInfo

class pk_itemdescriptionInfo(models.Model):
    id_item_name = models.ForeignKey(pk_itemInfo, on_delete=models.CASCADE, related_name='id_item_name',
                                     db_column='id_item_name')
    id_item_description = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["id_item_description"]

    def __str__(self):
        return self.id_item_description