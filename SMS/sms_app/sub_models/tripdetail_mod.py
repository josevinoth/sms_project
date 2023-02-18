from django.db import models
from ..models import MyUser,VehiclenumberInfo,VehicletypeInfo,VehiclesourceInfo,TrbusinesstypeInfo,City,StatusList

class TripdetailInfo(models.Model):
    tr_enquirynumber = models.CharField(max_length=10,default = '')
    tr_consignmentnumber = models.CharField(max_length=10,default = '')
    tr_tripnumber = models.CharField(max_length=10,default = '')
    tr_transportbusinesstype = models.ForeignKey(TrbusinesstypeInfo, on_delete=models.CASCADE, default='')
    tr_vehiclesource = models.ForeignKey(VehiclesourceInfo, on_delete=models.CASCADE, default='')
    tr_vehicletype = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='')
    tr_vehiclenumber = models.ForeignKey(VehiclenumberInfo, on_delete=models.CASCADE, default='')
    tr_drivername = models.CharField(max_length=30,null=True,blank=True)
    tr_drivernumber = models.CharField(max_length=30,null=True,blank=True)
    tr_fromlocation = models.ForeignKey(City,on_delete=models.CASCADE,related_name='tr_fromlocation', db_column='tr_fromlocation')
    tr_startingkm = models.IntegerField(default='')
    tr_startingdate = models.DateField(null=True,blank=True)
    tr_sealnumber = models.IntegerField(default='')
    tr_containernumber = models.IntegerField(default='')
    tr_tolocation = models.ForeignKey(City,on_delete=models.CASCADE,related_name='tr_tolocation', db_column='tr_tolocation')
    tr_endingkm = models.CharField(max_length=10,default = '')
    tr_endingdate = models.DateField(null=True,blank=True)
    tr_shipmentdetails = models.CharField(max_length=10,default = '')
    tr_status = models.ForeignKey(StatusList,on_delete=models.CASCADE, related_name='tr_status', db_column='tr_status')
    tr_updated_at = models.DateTimeField(null=True, auto_now=True)
    tr_created_at = models.DateTimeField(null=True, auto_now_add=True)
    tr_updated_by = models.ForeignKey(MyUser, related_name='tr_updated_by', db_column='tr_updated_by',
                                      on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.tr_tripnumber