from django.db import models
from ..models import MyUser,TrbusinesstypeInfo,VehiclesourceInfo,VehicletypeInfo,VehiclenumberInfo,StatusList

class VehicledetailInfo(models.Model):
    ve_enquirynumber = models.CharField(max_length=10,default = '')
    ve_consignmentnumber = models.CharField(max_length=10,default = '')
    ve_transportbusinesstype = models.ForeignKey(TrbusinesstypeInfo, on_delete=models.CASCADE, default='')
    ve_vehiclesource = models.ForeignKey(VehiclesourceInfo, on_delete=models.CASCADE, default='')
    ve_vehicletype = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='')
    ve_vehiclenumber = models.ForeignKey(VehiclenumberInfo, on_delete=models.CASCADE, default='')
    ve_drivername = models.CharField(max_length=30)
    ve_drivernumber = models.CharField(max_length=30)
    ve_status = models.ForeignKey(StatusList,on_delete=models.CASCADE, default='')
    ve_updated_at = models.DateTimeField(null=True, auto_now=True)
    ve_created_at = models.DateTimeField(null=True, auto_now_add=True)
    ve_updated_by = models.ForeignKey(MyUser, related_name='ve_updated_by', db_column='ve_updated_by',
                                      on_delete=models.CASCADE, null=True)




    # def __str__(self):
    #     return self.asset_number