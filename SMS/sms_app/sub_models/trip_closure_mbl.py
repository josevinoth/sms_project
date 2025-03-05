from django.db import models
from ..models import TripdetailInfo,Places,Tripstatusinfo

def trip_mbl_attach_path(instance, filename):
    return 'trmattachfiles/{0}/{1}'.format(instance.trm_tripnumber, filename)
class Trclosure_mblInfo(models.Model):
    trm_tripnumber = models.ForeignKey(TripdetailInfo, on_delete=models.CASCADE, default='')
    trm_departedlocation = models.ForeignKey(Places,on_delete=models.CASCADE,related_name='trm_departedlocation', db_column='trm_departedlocation',null=True, blank=True)
    trm_reportedlocation = models.ForeignKey(Places,on_delete=models.CASCADE,related_name='trm_reportedlocation', db_column='trm_reportedlocation',null=True, blank=True)
    trm_departeddate = models.DateTimeField(null=True, blank=True)
    trm_status = models.ForeignKey(Tripstatusinfo,on_delete=models.CASCADE, related_name='trm_status', db_column='trm_status',default=1)
    trm_attachment = models.FileField(upload_to=trip_mbl_attach_path, null=True,blank=True)

    class Meta:
        ordering = ["trm_tripnumber"]
    def __str__(self):
        return self.trm_tripnumber