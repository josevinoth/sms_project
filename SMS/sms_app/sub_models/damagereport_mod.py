from django.db import models
from ..models import DamageInfo
class DamagereportInfo(models.Model):
    dam_damage_type = models.ForeignKey(DamageInfo, on_delete=models.CASCADE, default='')
    dam_GRN_num = models.CharField(max_length=20, null=True,default='')

    def __str__(self):
        return self.dam_damage_type