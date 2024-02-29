from django.db import models
from ..models import iou_info,EnquirynoteInfo,ConsignmentdetailInfo,MyUser,VehiclemasterInfo,VehicletypeInfo,OwnershipInfo,Places,Tripstatusinfo
class Trip_category_info(models.Model):
    category = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["category"]

    def __str__(self):
        return self.category
class TripdetailInfo(models.Model):
    tr_enquirynumber = models.ForeignKey(EnquirynoteInfo, on_delete=models.CASCADE, default='')
    tr_consignmentnumber = models.ForeignKey(ConsignmentdetailInfo, on_delete=models.CASCADE, default='')
    tr_tripnumber = models.CharField(max_length=10,default = '',blank=True,null=True)
    tr_vehiclesource = models.ForeignKey(OwnershipInfo, on_delete=models.CASCADE, default='')
    tr_vehicletype = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='',related_name='tr_vehicletype', db_column='tr_vehicletype')
    tr_vehicletype_placed = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='',related_name='tr_vehicletype_placed', db_column='tr_vehicletype_placed')
    tr_vehicletype_selection_requested= models.BooleanField(blank=True,null=True)
    tr_vehicletype_selection_placed= models.BooleanField(blank=True,null=True)
    tr_vehiclenumber = models.ForeignKey(VehiclemasterInfo, on_delete=models.CASCADE, default='')
    tr_drivername = models.CharField(max_length=30,null=True,blank=True)
    tr_driver_lic = models.CharField(max_length=100,null=True,blank=True)
    tr_drivernumber = models.CharField(max_length=30,null=True,blank=True)
    tr_departedlocation = models.ForeignKey(Places,on_delete=models.CASCADE,related_name='tr_departedlocation', db_column='tr_departedlocation',null=True, blank=True)
    tr_departedkm = models.IntegerField(default=0,null=True, blank=True)
    tr_departeddate = models.DateTimeField(null=True, blank=True)
    tr_reportedlocation = models.ForeignKey(Places,on_delete=models.CASCADE,related_name='tr_reportedlocation', db_column='tr_reportedlocation',null=True, blank=True)
    tr_reportedkm = models.IntegerField(default =0,null=True, blank=True)
    tr_reporteddate = models.DateTimeField(null=True, blank=True)
    # tr_status = models.ForeignKey(Tripstatusinfo,on_delete=models.CASCADE, related_name='tr_status', db_column='tr_status',default=1)
    tr_updated_at = models.DateTimeField(null=True, auto_now=True)
    tr_created_at = models.DateTimeField(null=True, auto_now_add=True)
    tr_updated_by = models.ForeignKey(MyUser, related_name='tr_updated_by', db_column='tr_updated_by',on_delete=models.CASCADE, null=True)
    tr_category = models.ForeignKey(Trip_category_info, related_name='tr_category', db_column='tr_category',on_delete=models.CASCADE, null=True)
    tr_remarks=models.TextField(max_length=500,blank=True, null=True)
    tr_loading_time = models.DateTimeField(null=True, blank=True)
    tr_unloading_time = models.DateTimeField(null=True, blank=True)
    tr_iou = models.ForeignKey(iou_info, related_name='tr_iou', db_column='tr_iou', on_delete=models.CASCADE, null=True,blank=True)

    tc_tripcost = models.FloatField(default=0.0)
    tc_parkingcost = models.FloatField(default=0.0)
    tc_tollcost = models.FloatField(default=0.0)
    tc_loadingcost = models.FloatField(default=0.0)
    tc_unloadingcost = models.FloatField(default=0.0)
    tc_weighmentcost = models.FloatField(default=0.0)
    tc_handlingcost = models.FloatField(default=0.0)
    tc_pod = models.FloatField(default=0.0)
    tc_financestatus = models.ForeignKey(Tripstatusinfo, on_delete=models.CASCADE, default=1)

    class Meta:
        ordering = ["tr_tripnumber"]
    def __str__(self):
        return self.tr_tripnumber
def trip_closure_directory_path(instance, filename):

    return 'Tripclosurefiles/{0}/{1}'.format(instance.tcf_tripnumber, filename)
class Trip_closure_files_Info(models.Model):
    tcf_tripnumber = models.CharField(max_length=300, null=True,blank=True)
    tcf_trip_cost = models.FileField(upload_to=trip_closure_directory_path, null=True,blank=True)
    tcf_parking_cost = models.FileField(upload_to=trip_closure_directory_path, null=True,blank=True)
    tcf_toll_cost = models.FileField(upload_to=trip_closure_directory_path, null=True,blank=True)
    tcf_loading_cost = models.FileField(upload_to=trip_closure_directory_path, null=True,blank=True)
    tcf_unloading_cost = models.FileField(upload_to=trip_closure_directory_path, null=True,blank=True)
    tcf_weighment_cost = models.FileField(upload_to=trip_closure_directory_path, null=True,blank=True)
    tcf_handling_cost = models.FileField(upload_to=trip_closure_directory_path, null=True,blank=True)
    tcf_pod = models.FileField(upload_to=trip_closure_directory_path, null=True,blank=True)
