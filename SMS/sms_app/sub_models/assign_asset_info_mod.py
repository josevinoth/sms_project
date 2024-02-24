from django.db import models
from ..models import AssetInfo

class Assign_asset_info(models.Model):
    AA_asset_number = models.ForeignKey(AssetInfo, on_delete=models.CASCADE, blank=True, null=True,max_length=20)
    AA_assingedto = models.CharField(blank=True, null=True, max_length=20)
    AA_assignedon= models.CharField(blank=True, null=True, max_length=20)
    AA_assignedby = models.CharField(blank=True, null=True, max_length=20)
    AA_remarks =  models.CharField(blank=True, null=True, max_length=50)