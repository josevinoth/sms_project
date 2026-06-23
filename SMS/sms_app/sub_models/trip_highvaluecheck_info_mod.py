from django.db import models
from ..models import YesNoInfo,EnquirynoteInfo,TripdetailInfo,ConsignmentdetailInfo,approval_status_info

class TripHighvalueInfo(models.Model):
    thc_enquirynumber = models.ForeignKey(EnquirynoteInfo, on_delete=models.CASCADE, default='')
    thc_tripnumber = models.ForeignKey(TripdetailInfo, on_delete=models.CASCADE, default='')
    thc_vehicleRC = models.ForeignKey(YesNoInfo, related_name='thc_vehicleRC', db_column='thc_vehicleRC',on_delete=models.CASCADE,default=2)
    thc_vehicle_insurance = models.ForeignKey(YesNoInfo, related_name='thc_vehicle_insurance', db_column='thc_vehicle_insurance',on_delete=models.CASCADE, default=2)
    thc_goodspermit = models.ForeignKey(YesNoInfo, related_name='thc_goodspermit', db_column='thc_goodspermit',on_delete=models.CASCADE, default=2)
    thc_outside_undercarriage = models.ForeignKey(YesNoInfo, related_name='thc_outside_undercarriage', db_column='thc_outside_undercarriage',on_delete=models.CASCADE, default=2)
    thc_inoutside_doors = models.ForeignKey(YesNoInfo, related_name='thc_inoutside_doors', db_column='thc_inoutside_doors',on_delete=models.CASCADE, default=2)
    thc_rightinnerwall = models.ForeignKey(YesNoInfo, related_name='thc_rightinnerwall', db_column='thc_rightinnerwall',on_delete=models.CASCADE, default=2)
    thc_leftinnerwall = models.ForeignKey(YesNoInfo, related_name='thc_leftinnerwall', db_column='thc_leftinnerwall',on_delete=models.CASCADE, default=2)
    thc_frontinnerwall = models.ForeignKey(YesNoInfo, related_name='thc_frontinnerwall', db_column='thc_frontinnerwall',on_delete=models.CASCADE, default=2)
    thc_roof = models.ForeignKey(YesNoInfo, related_name='thc_roof', db_column='thc_roof',on_delete=models.CASCADE, default=2)
    thc_floorinside = models.ForeignKey(YesNoInfo, related_name='thc_floorinside', db_column='thc_floorinside',on_delete=models.CASCADE, default=2)
    thc_gpsfit = models.ForeignKey(YesNoInfo, related_name='thc_gpsfit', db_column='thc_gpsfit',on_delete=models.CASCADE, default=2)
    thc_simtracking = models.ForeignKey(YesNoInfo, related_name='thc_simtracking', db_column='thc_simtracking',on_delete=models.CASCADE, default=2)
    thc_smartlock = models.ForeignKey(YesNoInfo, related_name='thc_smartlock', db_column='thc_smartlock',on_delete=models.CASCADE, default=2)
    thc_smartlockbaterry = models.ForeignKey(YesNoInfo, related_name='thc_smartlockbaterry', db_column='thc_smartlockbaterry',on_delete=models.CASCADE, default=2)
    thc_bottle_otlseal = models.ForeignKey(YesNoInfo, related_name='thc_bottle_otlseal', db_column='thc_bottle_otlseal',on_delete=models.CASCADE, default=2)
    thc_commercialinvoice = models.ForeignKey(YesNoInfo, related_name='thc_commercialinvoice', db_column='thc_commercialinvoice',on_delete=models.CASCADE, default=2)
    thc_packinglist = models.ForeignKey(YesNoInfo, related_name='thc_packinglist', db_column='thc_packinglist',on_delete=models.CASCADE, default=2)
    thc_eipl_coc = models.ForeignKey(YesNoInfo, related_name='thc_eipl_coc', db_column='thc_eipl_coc',on_delete=models.CASCADE, default=2)
    thc_consignmentnote = models.ForeignKey(YesNoInfo, related_name='thc_consignmentnote', db_column='thc_consignmentnote',on_delete=models.CASCADE, default=2)
    thc_ewaybill = models.ForeignKey(YesNoInfo, related_name='thc_ewaybill', db_column='thc_ewaybill',on_delete=models.CASCADE, default=2)
    thc_packagesloaded = models.IntegerField(default=0)
    thc_remarks = models.TextField(max_length=50, blank=True, null=True)
    thc_approval_status = models.ForeignKey(approval_status_info, on_delete=models.CASCADE, blank=True, null=True,default=2)
    thc_vehiclenumber = models.CharField(max_length=10,blank=True,null=True)

    def __str__(self):
        return str(self.thc_tripnumber) if self.thc_tripnumber else "N/A"