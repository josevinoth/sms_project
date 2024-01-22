from django.db import models
from ..models import Check_in_out,CustomerInfo,Labels_pasted_Info,StatusList,VehicletypeInfo,GstexcemptionInfo,MyUser

class Dispatch_info(models.Model):
    dispatch_depature_date = models.DateTimeField(null=True,blank=True)
    dispatch_driver = models.CharField(null=False, max_length=20)
    dispatch_contact_number = models.CharField(null=False, max_length=20)
    dispatch_DL_number = models.CharField(null=False, max_length=20)
    dispatch_otl = models.CharField(null=False, max_length=20)
    dispatch_transporter = models.CharField(null=False, max_length=100)
    dispatch_truck_number = models.CharField(null=False, max_length=20)
    dispatch_truck_type = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='',related_name='dispatch_truck_type',db_column='dispatch_truck_type')
    dispatch_truck_type_billing = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='',related_name='dispatch_truck_type_billing',db_column='dispatch_truck_type_billing',null=True,blank=True)
    dispatch_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6,null=False)
    dispatch_sticker_pasted_bvm= models.ForeignKey(Labels_pasted_Info, on_delete=models.CASCADE,null=True,blank=True,related_name='dispatch_sticker_pasted_bvm', db_column='dispatch_sticker_pasted_bvm')
    # dispatch_destination = models.CharField(null=False, max_length=20)
    dispatch_comments = models.TextField(null=False,blank=True,max_length=300,default="Goods In Good Condition")
    dispatch_cargo_picked = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE,null=False,related_name='dispatch_cargo_picked', db_column='dispatch_cargo_picked')
    dispatch_num = models.CharField(null=False,blank=True,max_length=20)
    # dispatch_ewaybill = models.CharField(null=False, max_length=30)
    dispatch_created_at = models.DateTimeField(null=True, auto_now_add=True)
    dispatch_updated_at = models.DateTimeField(null=True, auto_now=True)
    dispatch_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    dispatch_mawb = models.CharField(null=True,blank=True, max_length=100)
    dispatch_invoice_list = models.CharField(null=True,blank=True, max_length=100000)
    dispatch_job_num_list = models.CharField(null=True,blank=True, max_length=100000)
    dispatch_total_weight = models.FloatField(null=True,blank=True,default=0.0)
    dispatch_total_goods = models.IntegerField(null=True,blank=True,default=0)
    dispatch_customer = models.ForeignKey(CustomerInfo,on_delete=models.CASCADE, default='',blank=True, null=True)
    dispatch_billing_truck_type = models.ForeignKey(Check_in_out, on_delete=models.CASCADE, default='',
                                                    related_name='dispatch_billing_truck_type',
                                                    db_column='dispatch_billing_truck_type', null=True, blank=True)