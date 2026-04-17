from django.db import models
from ..models import Check_in_out,CustomerInfo,Labels_pasted_Info,StatusList,VehicletypeInfo,GstexcemptionInfo,MyUser,TransitdistributeInfo
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>

    return 'DispatchsignImages/{0}/{1}'.format(instance.dispatch_num, filename)

class Dispatch_info(models.Model):
    dispatch_depature_date = models.DateTimeField(null=True,blank=True)
    dispatch_driver = models.CharField(null=False, max_length=20)
    dispatch_contact_number = models.CharField(null=False, max_length=20)
    dispatch_DL_number = models.CharField(null=False, max_length=20)
    dispatch_otl = models.CharField(null=False, max_length=20)
    dispatch_transporter = models.CharField(null=False, max_length=100)
    dispatch_gatein_time = models.DateTimeField(null=True, blank=True)
    dispatch_dockin_time = models.DateTimeField(null=True, blank=True)
    dispatch_dockout_time = models.DateTimeField(null=True, blank=True)
    dispatch_truck_number = models.CharField(null=False, max_length=20)
    dispatch_truck_type = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='',related_name='dispatch_truck_type',db_column='dispatch_truck_type')
    dispatch_truck_type_billing = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='',related_name='dispatch_truck_type_billing',db_column='dispatch_truck_type_billing',null=True,blank=True)
    dispatch_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6,null=False)
    dispatch_sticker_pasted_bvm= models.ForeignKey(Labels_pasted_Info, on_delete=models.CASCADE,null=True,blank=True,related_name='dispatch_sticker_pasted_bvm', db_column='dispatch_sticker_pasted_bvm')
    # dispatch_destination = models.CharField(null=False, max_length=20)
    dispatch_comments = models.TextField(null=False,blank=True,max_length=300,default="All Goods Received and In Good Condition")
    dispatch_cargo_picked = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE,null=False,related_name='dispatch_cargo_picked', db_column='dispatch_cargo_picked',default=1)
    dispatch_num = models.CharField(null=False,blank=True,max_length=50)
    # dispatch_ewaybill = models.CharField(null=False, max_length=30)
    dispatch_created_at = models.DateTimeField(null=True, auto_now_add=True)
    dispatch_updated_at = models.DateTimeField(null=True, auto_now=True)
    dispatch_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    dispatch_mawb = models.CharField(null=True,blank=True, max_length=100)
    dispatch_invoice_list = models.CharField(null=True,blank=True, max_length=100000)
    dispatch_job_num_list = models.CharField(null=True,blank=True, max_length=100000)
    dispatch_total_weight = models.FloatField(null=True,blank=True,default=0.0)
    dispatch_total_goods = models.IntegerField(null=True,blank=True,default=0)
    dispatch_customer = models.ForeignKey(CustomerInfo,on_delete=models.CASCADE)
    dispatch_billing_truck_type = models.ForeignKey(Check_in_out, on_delete=models.CASCADE, default=3,
                                                       related_name='dispatch_billing_truck_type',
                                                    db_column='dispatch_billing_truck_type', null=True, blank=True)
    dispatch_email_count = models.IntegerField(null=True,blank=True,default=0)
    dispatch_transit = models.ForeignKey(TransitdistributeInfo,on_delete=models.CASCADE, null=True, blank=True)
    dispatch_reference = models.CharField(null=True,blank=True, max_length=40)
    dispatch_driver_signature = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    dispatch_supervisor_signature = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    dispatch_gatepass_att = models.FileField(upload_to=user_directory_path, null=True, blank=True)

    def __str__(self):
        return str(self.dispatch_num) if self.dispatch_num else "N/A"