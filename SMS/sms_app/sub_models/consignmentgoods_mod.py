from django.db import models

from .Consignmenttype_mod import Consignment_type
from ..models import Stock_type,ConsignmentdetailInfo,Currency_type,MyUser,ConsignerInfo,ConsigneeInfo

def consignmentgoods_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'Consignment_Goods_files/{0}/{1}'.format(instance.cg_consignmentnumber, filename)
class ConsignmentgoodsInfo(models.Model):
    cg_currency_type = models.ForeignKey(Currency_type, on_delete=models.CASCADE,default=1,blank=True,null=True)
    cg_consigner = models.ForeignKey(ConsignerInfo, on_delete=models.CASCADE,blank=True,null=True)
    cg_consignee = models.ForeignKey(ConsigneeInfo, on_delete=models.CASCADE,blank=True,null=True)
    cg_consignerinvoice = models.CharField(max_length=150)
    cg_consignerinvoice_date = models.DateField()
    cg_consignervalue = models.FloatField(null=True, blank=True)
    cg_valueininr = models.FloatField(null=True, blank=True)
    cg_ebillno = models.CharField(max_length=12, null=True, blank=True)
    cg_dateofissue = models.DateField(blank=True,null=True)
    cg_dateofvalidity = models.DateField(blank=True,null=True)
    cg_height = models.IntegerField(blank=True, null=True, default=0)
    cg_width = models.IntegerField(blank=True, null=True, default=0)
    cg_length = models.IntegerField(blank=True, null=True, default=0)
    cg_qty = models.IntegerField(default=0)
    cg_loaded_qty = models.IntegerField(default=0)
    cg_weight = models.FloatField(default=0.0)
    cg_lastmodifiedby = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True,blank=True)
    cg_created_at = models.DateTimeField(null=True,blank=True, auto_now_add=True)
    cg_updated_at = models.DateTimeField(null=True,blank=True, auto_now=True)
    cg_consignmentnumber = models.ForeignKey(ConsignmentdetailInfo, on_delete=models.CASCADE,blank=True,null=True,related_name='cg_consignmentnumber',db_column='cg_consignmentnumber')
    cg_description = models.ForeignKey(Stock_type, on_delete=models.CASCADE,blank=True,null=True,related_name='cg_description',db_column='cg_description')
    cg_arrival_date = models.DateTimeField(null=True,blank=True)
    cg_unloading_date = models.DateTimeField(null=True,blank=True)
    cg_ewaybill_att = models.FileField(upload_to=consignmentgoods_directory_path, null=True, blank=True)
    cg_invoice_att = models.FileField(upload_to=consignmentgoods_directory_path, null=True, blank=True)
    cg_otl_att = models.FileField(upload_to=consignmentgoods_directory_path, null=True, blank=True)
    cg_hawbno = models.CharField(max_length=1000,default = '', null=True, blank=True)
    cg_consignmenttype = models.ForeignKey(Consignment_type, on_delete=models.CASCADE,default=1, null=True,blank=True)
    cg_mawbno = models.CharField(max_length=11, default='', null=True, blank=True)


    def __str__(self):
        return self.cg_consignmentnumber