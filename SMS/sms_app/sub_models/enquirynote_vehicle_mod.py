from django.db import models
from ..models import MyUser,VehicletypeInfo,EnquirynoteInfo,VehiclecategoryInfo

class Enquirynotevehicle(models.Model):
    env_enquirynumber = models.ForeignKey(EnquirynoteInfo, on_delete=models.CASCADE, default='')
    env_vehicletype = models.ForeignKey(VehicletypeInfo,on_delete=models.CASCADE, default='')
    env_quantity = models.IntegerField(blank=True, null=True, default=0)
    env_vehiclecategory = models.ForeignKey(VehiclecategoryInfo,on_delete=models.CASCADE, default='')
    env_created_at = models.DateField(null=True, auto_now_add=True)
    env_updated_at = models.DateField(null=True, auto_now=True)
    env_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='env_updated_by',db_column='env_updated_by', null=True)


    class Meta:
        ordering = ["env_enquirynumber"]

    def __str__(self):
        return self.env_enquirynumber