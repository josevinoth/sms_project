from django.db import models
from ..models import Tr_triptype_Info,MovementtypeInfo,Tr_businesstype_Info,CustomerInfo,CustomerdepartmentInfo,MyUser,VehiclecategoryInfo,VehicletypeInfo,StatusList,Places

class EnquirynoteInfo(models.Model):
    en_enquirynumber = models.CharField(max_length=100,null=True,blank=True)
    en_customername = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, default='')
    en_customerdepartment = models.ForeignKey(CustomerdepartmentInfo, on_delete=models.CASCADE, default='')
    en_vehiclecategory = models.ForeignKey(VehiclecategoryInfo,on_delete=models.CASCADE, default='')
    en_vehicletype = models.ForeignKey(VehicletypeInfo,on_delete=models.CASCADE, default='')
    en_assignedto = models.ForeignKey(MyUser,on_delete=models.CASCADE, default='')
    en_status = models.ForeignKey(StatusList,on_delete=models.CASCADE, default=6)
    en_updatedon = models.DateTimeField(null=True, auto_now=True)
    en_created_at = models.DateTimeField(null=True, auto_now_add=True)
    en_updated_by = models.ForeignKey(MyUser, related_name='en_updated_by', db_column='en_updated_by',on_delete=models.CASCADE, null=True)
    en_consignmentdetails = models.CharField(max_length=1000,null=True,blank=True)
    en_vehicledetails = models.CharField(max_length=100, null=True,blank=True)
    en_tripdetails = models.CharField(max_length=1000, null=True,blank=True)
    en_vehicle_allotment = models.CharField(max_length=1000, null=True,blank=True)
    en_tripclosure = models.CharField(max_length=1000, null=True,blank=True)
    en_pickupdatetime =  models.DateTimeField(null=True, blank=True)
    en_business_type = models.ForeignKey(Tr_businesstype_Info, on_delete=models.CASCADE, default="",null=True,blank=True)
    en_movement_type = models.ForeignKey(MovementtypeInfo, on_delete=models.CASCADE, default="",null=True,blank=True)
    en_trip_type = models.ForeignKey(Tr_triptype_Info, on_delete=models.CASCADE, default="",null=True,blank=True)
    en_fromlocaion = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='en_fromlocaion',db_column='en_fromlocaion', null=True, blank=True)
    en_tolocation = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='en_tolocation',db_column='en_tolocation', null=True, blank=True)
    en_touchpoint = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='en_touchpoint',db_column='en_touchpoint', null=True, blank=True)
    en_touchpoint2 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='en_touchpoint2',db_column='en_touchpoint2', null=True, blank=True)
    en_touchpoint3 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='en_touchpoint3',db_column='en_touchpoint3', null=True, blank=True)
    en_touchpoint4 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='en_touchpoint4',db_column='en_touchpoint4', null=True, blank=True)
    def __str__(self):
        return self.en_enquirynumber