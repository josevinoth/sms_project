from django.db import models
from ..models import Stock_type,ConsignmentdetailInfo,Currency_type,MyUser

class ConsignmentgoodsInfo(models.Model):
    cg_currency_type = models.ForeignKey(Currency_type, on_delete=models.CASCADE,blank=True,null=True)
    cg_consigner = models.CharField(max_length=50,default = '')
    cg_consignee = models.CharField(max_length=50,default = '')
    cg_consignerinvoice = models.CharField(max_length=50)
    cg_consignerinvoice_date = models.DateField()
    cg_consignervalue = models.IntegerField(default='')
    cg_valueininr = models.IntegerField(default='')
    cg_noofpieces = models.IntegerField(default='')
    cg_weight = models.IntegerField(default='')
    cg_ebillno = models.CharField(max_length=10,default = '')
    cg_dateofissue = models.DateField(blank=True,null=True)
    cg_dateofvalidity = models.DateField(blank=True,null=True)
    cg_height = models.IntegerField(blank=True, null=True, default=0)
    cg_width = models.IntegerField(blank=True, null=True, default=0)
    cg_length = models.IntegerField(blank=True, null=True, default=0)
    cg_lastmodifiedby = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True,blank=True)
    cg_created_at = models.DateTimeField(null=True,blank=True, auto_now_add=True)
    cg_updated_at = models.DateTimeField(null=True,blank=True, auto_now=True)
    cg_consignmentnumber = models.ForeignKey(ConsignmentdetailInfo, on_delete=models.CASCADE,blank=True,null=True,related_name='cg_consignmentnumber',db_column='cg_consignmentnumber')
    cg_description = models.ForeignKey(Stock_type, on_delete=models.CASCADE,blank=True,null=True,related_name='cg_description',db_column='cg_description')
    cg_arrival_date = models.DateTimeField(null=True,blank=True)
    cg_unloading_date = models.DateTimeField(null=True,blank=True)


    def __str__(self):
        return self.cg_consignmentnumber