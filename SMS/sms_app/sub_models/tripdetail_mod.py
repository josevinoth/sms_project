from django.db import models
from ..models import Trip_approval_info,iou_info,EnquirynoteInfo,ConsignmentdetailInfo,MyUser,VehicletypeInfo,OwnershipInfo,Places,Tripstatusinfo,YesNoInfo

def trip_attach_path(instance, filename):
    return 'PODattachfiles/{0}/{1}'.format(instance.tr_tripnumber, filename)
def pod_digi_sign_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'PODsignImages/{0}/{1}'.format(instance.tr_tripnumber, filename)

class Trip_category_info(models.Model):
    category = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["category"]

    def __str__(self):
        return self.category
class TripdetailInfo(models.Model):
    tr_enquirynumber = models.ForeignKey(EnquirynoteInfo, on_delete=models.CASCADE, default='')
    tr_consignmentnumber = models.ForeignKey(ConsignmentdetailInfo, on_delete=models.CASCADE, null=True,blank=True)
    tr_tripnumber = models.CharField(max_length=10,default = '',blank=True,null=True)
    tr_vehiclesource = models.ForeignKey(OwnershipInfo, on_delete=models.CASCADE, default='')
    tr_vehicletype = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='',related_name='tr_vehicletype', db_column='tr_vehicletype')
    tr_vehicletype_placed = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='',related_name='tr_vehicletype_placed', db_column='tr_vehicletype_placed')
    tr_vehicletype_selection_requested= models.BooleanField(blank=True,null=True)
    tr_vehicletype_selection_placed= models.BooleanField(blank=True,null=True)
    tr_vehiclenumber = models.CharField(max_length=10,blank=True,null=True)
    tr_drivername = models.CharField(max_length=30,null=True,blank=True)
    tr_driver_lic = models.CharField(max_length=100,null=True,blank=True)
    tr_drivernumber = models.CharField(max_length=30,null=True,blank=True)
    tr_departedlocation = models.ForeignKey(Places,on_delete=models.CASCADE,related_name='tr_departedlocation', db_column='tr_departedlocation',null=True, blank=True)
    tr_departedkm = models.IntegerField(null=True, blank=True)
    tr_departeddate = models.DateTimeField(null=True, blank=True)
    tr_reportedlocation = models.ForeignKey(Places,on_delete=models.CASCADE,related_name='tr_reportedlocation', db_column='tr_reportedlocation',null=True, blank=True)
    tr_reportedkm = models.IntegerField(null=True, blank=True)
    tr_reporteddate = models.DateTimeField(null=True, blank=True)
    # tr_status = models.ForeignKey(Tripstatusinfo,on_delete=models.CASCADE, related_name='tr_status', db_column='tr_status',default=1)
    tr_updated_at = models.DateTimeField(null=True, auto_now=True)
    tr_created_at = models.DateTimeField(null=True, auto_now_add=True)
    tr_updated_by = models.ForeignKey(MyUser, related_name='tr_updated_by', db_column='tr_updated_by',on_delete=models.CASCADE, null=True)
    tr_category = models.ForeignKey(Trip_category_info, related_name='tr_category', db_column='tr_category',on_delete=models.CASCADE, null=True)
    tr_remarks=models.TextField(max_length=250,blank=True, null=True)
    tr_loading_time = models.DateTimeField(null=True, blank=True)
    tr_unloading_time = models.DateTimeField(null=True, blank=True)
    tr_iou = models.ForeignKey(iou_info, related_name='tr_iou', db_column='tr_iou', on_delete=models.CASCADE, null=True,blank=True)
    tr_dock_in_time = models.DateTimeField(null=True, blank=True)
    tr_dock_out_time = models.DateTimeField(null=True, blank=True)
    tr_approval = models.ForeignKey(Trip_approval_info, on_delete=models.SET_NULL, null=True, blank=True)
    tr_departeddate_pickup = models.DateTimeField(null=True, blank=True)
    tr_departeddate_delivery = models.DateTimeField(null=True, blank=True)
    tr_reportedkm_pickup = models.IntegerField(null=True, blank=True)
    tr_reporteddate_pickup = models.DateTimeField(null=True, blank=True)
    tr_reportedkm_delivery = models.IntegerField(null=True, blank=True)
    tr_reporteddate_delivery = models.DateTimeField(null=True, blank=True)

    tc_tripcost = models.FloatField(default=0.0)
    tc_parkingcost = models.FloatField(default=0.0)
    tc_tollcost = models.FloatField(default=0.0)
    tc_loadingcost = models.FloatField(default=0.0)
    tc_unloadingcost = models.FloatField(default=0.0)
    tc_weighmentcost = models.FloatField(default=0.0)
    tc_handlingcost = models.FloatField(default=0.0)
    tc_haltingcost = models.FloatField(default=0.0)
    tc_total_halting_cost = models.FloatField(default=0.0)
    tc_supervisorcost = models.FloatField(default=0.0)
    tc_no_of_days_halting = models.IntegerField(null=True, blank=True,default=0)
    tc_pod = models.CharField(default=" ")
    tc_financestatus = models.ForeignKey(Tripstatusinfo, on_delete=models.CASCADE,blank=True,null=True)
    tc_pod_attachment = models.FileField(upload_to=trip_attach_path, null=True,blank=True)
    tr_customerref = models.CharField(max_length=30,null=True,blank=True)
    tr_high_value = models.ForeignKey(YesNoInfo, on_delete=models.CASCADE, related_name='tr_high_value',db_column='tr_high_value', default=2)
    tr_track_link = models.URLField(max_length=500,null=True,blank=True,verbose_name="Tracking Link")
    td_pod = models.ImageField(upload_to=pod_digi_sign_path, null=True, blank=True)

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
