from django.db import models
from ..models import CustomerInfo,Nadimension,pk_itemdescriptionInfo,pk_itemInfo,PkstockpurchasesInfo,Pkstocktype,MyUser,Costtype,Stockdescription,Unitofmeasure,PkneedassessmentInfo,Nadimensiontype

class PkquotationInfo(models.Model):
    pkqt_cost_type = models.ForeignKey(Costtype, on_delete=models.CASCADE, default='')
    pkqt_stock_description = models.ForeignKey(Stockdescription, on_delete=models.CASCADE, blank=True, null=True)
    pkqt_width = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_height = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_cft = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_rate = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_days = models.IntegerField(blank=True, null=True, default=0)
    pkqt_total_cost = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_created_at = models.DateTimeField(null=True, auto_now_add=True)
    pkqt_updated_at = models.DateTimeField(null=True, auto_now=True)
    pkqt_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='pkqt_updated_by',
                                      db_column='pkqt_updated_by', null=True)
    pkqt_quantity = models.FloatField(blank=True, null=True, default=0)
    pkqt_size = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_uom = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE,related_name='pkqt_uom', db_column='pkqt_uom', default='', blank=True, null=True)
    pkqt_assessment_num = models.ForeignKey(PkneedassessmentInfo, on_delete=models.CASCADE, default='', blank=True,
                                          null=True)
    pkqt_length = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_stock_type = models.ForeignKey(Pkstocktype, on_delete=models.CASCADE, blank=True, null=True)
    pkqt_stock_purchase_number = models.ForeignKey(PkstockpurchasesInfo, on_delete=models.CASCADE, blank=True, null=True)
    pkqt_item = models.ForeignKey(pk_itemInfo, on_delete=models.CASCADE, related_name='pkqt_item', db_column='pkqt_item',
                                blank=True, null=True)
    pkqt_itemdescription = models.ForeignKey(pk_itemdescriptionInfo, on_delete=models.CASCADE,
                                           related_name='pkqt_itemdescription', db_column='pkqt_itemdescription',
                                           blank=True, null=True)
    pkqt_requirement = models.ForeignKey(Nadimension, on_delete=models.CASCADE, blank=True, null=True,
                                       related_name='pkqt_requirement', db_column='pkqt_requirement', )
    pkqt_requirement_size = models.CharField(max_length=100, null=True, blank=True)
    pkqt_width_req = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_height_req = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_length_req = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, related_name='pkqt_customer_name',
                                         db_column='pkqt_customer_name', blank=True, null=True)
    pkqt_dimension_type = models.ForeignKey(Nadimensiontype,on_delete=models.CASCADE,blank=True,null=True,default='')
    pkqt_width_boxod = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_height_boxod = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_length_boxod = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_box_id_clearance_l = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_box_id_clearance_w = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_box_id_clearance_h = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_box_od_clearance_l = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_box_od_clearance_w = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_box_od_clearance_h = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_uom_calc = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE, default='',related_name='pkqt_uom_calc', db_column='pkqt_uom_calc', limit_choices_to={'id__in': [1,2,3,4]},blank=True,null=True)
    pkqt_quantity_req= models.FloatField(blank=True, null=True, default=0.0)
    pkqt_sqrt_req = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_cft_req = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_totalbox_cost = models.FloatField(blank=True, null=True, default=0.0)
    pkqt_na_quantity = models.FloatField(blank=True, null=True, default=0.0)


    class Meta:
        ordering = ["pkqt_cost_type"]

    def __str__(self):
        return str(self.pkqt_cost_type)