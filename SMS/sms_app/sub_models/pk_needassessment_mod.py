from django.db import models
from ..models import StatusList,MyUser,Natypeofwork,Natypeofpack,Naplywoodthickness,CustomerInfo,Nawoodtreatmentreq,Nabvmcustomer,Nawoodnorms,VehicletypeInfo,Natypeofaccess,Naconsumables

class PkneedassessmentInfo(models.Model):
    na_assessment_num = models.CharField(max_length=100,null=True,blank=True, default='')
    na_date = models.DateField(blank=True, null=True)
    na_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, default='')
    na_type_of_work = models.ForeignKey(Natypeofwork,on_delete=models.CASCADE,default='')
    na_type_of_pack= models.ForeignKey(Natypeofpack,on_delete=models.CASCADE,default='')
    na_wood_treatment_req = models.ForeignKey(Nawoodtreatmentreq, on_delete=models.CASCADE, default='')
    na_unloading = models.ForeignKey(Nabvmcustomer,on_delete=models.CASCADE, related_name='na_unloading',db_column='na_unloading',default='')
    na_wood_norms =models.ForeignKey(Nawoodnorms,on_delete=models.CASCADE,default='')
    na_vehicle = models.ForeignKey(Nabvmcustomer,on_delete=models.CASCADE, related_name='na_vehicle',db_column='na_vehicle',default='')
    na_vehicle_type = models.ForeignKey(VehicletypeInfo,on_delete=models.CASCADE,default='')
    na_type_of_access = models.ForeignKey(Natypeofaccess,on_delete=models.CASCADE,default='')
    na_consumables = models.ForeignKey(Naconsumables,on_delete=models.CASCADE,default='')
    na_created_at = models.DateTimeField(null=True, auto_now_add=True)
    na_updated_at = models.DateTimeField(null=True, auto_now=True)
    na_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='na_updated_by',db_column='na_updated_by', null=True)
    na_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6,blank=True,null=True)
    class Meta:
        ordering = ["na_assessment_num"]

    def __str__(self):
        return self.na_assessment_num