from django.db import models
from ..models import City,StatusList

class TripdetailInfo(models.Model):
    tr_enquirynumber = models.CharField(max_length=10,default = '')
    tr_consignmentnumber = models.CharField(max_length=10,default = '')
    tr_tripnumber = models.CharField(max_length=10,default = '')
    tr_fromlocation = models.ForeignKey(City,on_delete=models.CASCADE,related_name='tr_fromlocation', db_column='tr_fromlocation')
    tr_startingkm = models.IntegerField(default='')
    tr_startingdate = models.CharField(max_length=30)
    tr_deliveryimages = models.CharField(max_length=30)
    tr_proofofdelivery = models.CharField(max_length=30)
    tr_sealnumber = models.IntegerField(default='')
    tr_containernumber = models.IntegerField(default='')
    tr_tripstatus = models.ForeignKey(StatusList,on_delete=models.CASCADE, related_name='tr_tripstatus', db_column='tr_tripstatus')
    tr_tolocation = models.ForeignKey(City,on_delete=models.CASCADE,related_name='tr_tolocation', db_column='tr_tolocation')
    tr_endingkm = models.CharField(max_length=10,default = '')
    tr_endingdate = models.CharField(max_length=10,default = '')
    tr_shipmentdetails = models.CharField(max_length=10,default = '')
    tr_status = models.ForeignKey(StatusList,on_delete=models.CASCADE, related_name='tr_status', db_column='tr_status')
    tr_lastmodifiedby = models.CharField(max_length=30)


    def __str__(self):
        return self.tr_tripnumber