from django.db import models
from ..models import Labels_pasted_Info,StatusList,VehicletypeInfo,GstexcemptionInfo,MyUser

class Dispatch_info(models.Model):
    dispatch_depature_date = models.DateTimeField(null=True,blank=True)
    dispatch_driver = models.CharField(null=False, max_length=20)
    dispatch_contact_number = models.CharField(null=False, max_length=20)
    dispatch_DL_number = models.CharField(null=False, max_length=20)
    dispatch_otl = models.CharField(null=False, max_length=20)
    dispatch_transporter = models.CharField(null=False, max_length=100)
    dispatch_truck_number = models.CharField(null=False, max_length=20)
    dispatch_truck_type = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='')
    dispatch_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6,null=False)
    dispatch_sticker_pasted_bvm= models.ForeignKey(Labels_pasted_Info, on_delete=models.CASCADE,null=True,blank=True,related_name='dispatch_sticker_pasted_bvm', db_column='dispatch_sticker_pasted_bvm')
    dispatch_destination = models.CharField(null=False, max_length=20)
    dispatch_comments = models.CharField(null=False, max_length=20)
    dispatch_cargo_picked = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE,null=False,related_name='dispatch_cargo_picked', db_column='dispatch_cargo_picked')
    dispatch_num = models.CharField(null=False, max_length=20)
    dispatch_eWaybill = models.CharField(null=False, max_length=30)
    dispatch_created_at = models.DateTimeField(null=True, auto_now_add=True)
    dispatch_updated_at = models.DateTimeField(null=True, auto_now=True)
    dispatch_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    dispatch_ship_date = models.DateTimeField(null=True, blank=True)
    dispatch_mawb = models.CharField(null=True, max_length=100)