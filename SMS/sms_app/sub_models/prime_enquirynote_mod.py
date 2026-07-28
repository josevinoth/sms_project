from django.db import models
from django.utils import timezone

from ..models import Tr_triptype_Info, MovementtypeInfo, Tr_businesstype_Info, CustomerInfo, CustomerdepartmentInfo, MyUser, VehiclecategoryInfo, VehicletypeInfo, StatusList, Places

class PrimeEnquirynoteInfo(models.Model):
    pen_enquirynumber = models.CharField(max_length=100, null=True, blank=True)
    pen_customername = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, default='')
    pen_customerdepartment = models.ForeignKey(CustomerdepartmentInfo, on_delete=models.CASCADE, default='', null=True, blank=True)
    pen_assignedto = models.ForeignKey(MyUser, on_delete=models.CASCADE, default='', null=True, blank=True)
    pen_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6)
    pen_updatedon = models.DateTimeField(null=True, auto_now=True)
    pen_created_at = models.DateTimeField(null=True, auto_now_add=True)
    pen_updated_by = models.ForeignKey(MyUser, related_name='pen_updated_by', db_column='pen_updated_by', on_delete=models.CASCADE, null=True)
    
    pen_consignmentdetails = models.CharField(max_length=1000, null=True, blank=True)
    pen_vehicledetails = models.CharField(max_length=100, null=True, blank=True)
    pen_tripdetails = models.CharField(max_length=1000, null=True, blank=True)
    pen_vehicle_allotment = models.CharField(max_length=1000, null=True, blank=True)
    pen_tripclosure = models.CharField(max_length=1000, null=True, blank=True)
    
    pen_pickupdatetime = models.DateTimeField(default=timezone.now, null=True, blank=True)
    pen_todatetime = models.DateTimeField(null=True, blank=True)
    
    pen_business_type = models.ForeignKey(Tr_businesstype_Info, on_delete=models.CASCADE, default=1, null=True, blank=True)
    pen_movement_type = models.ForeignKey(MovementtypeInfo, on_delete=models.CASCADE, default=1, null=True, blank=True)
    pen_trip_type = models.ForeignKey(Tr_triptype_Info, on_delete=models.CASCADE, null=True, blank=True)
    
    pen_fromlocaion = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='pen_fromlocaion', db_column='pen_fromlocaion', null=True, blank=True)
    pen_tolocation = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='pen_tolocation', db_column='pen_tolocation', null=True, blank=True)
    pen_touchpoint = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='pen_touchpoint', db_column='pen_touchpoint', null=True, blank=True)
    pen_touchpoint2 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='pen_touchpoint2', db_column='pen_touchpoint2', null=True, blank=True)
    pen_touchpoint3 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='pen_touchpoint3', db_column='pen_touchpoint3', null=True, blank=True)
    pen_touchpoint4 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='pen_touchpoint4', db_column='pen_touchpoint4', null=True, blank=True)
    
    pen_customer_new_name = models.CharField(blank=True, null=True, max_length=500)
    pen_contactno = models.CharField(max_length=10, default='', null=True, blank=True)
    pen_email = models.EmailField(max_length=50, default='', null=True, blank=True)
    pen_requestor = models.CharField(max_length=200, blank=True, null=True)

    # New fields for LP/Agent portal equivalent in prime
    pen_agent_name = models.CharField(max_length=200, null=True, blank=True)
    pen_vehicle_req_time = models.TimeField(null=True, blank=True)
    pen_no_of_vehicles = models.IntegerField(default=0, blank=True)
    pen_agreed_km = models.FloatField(default=0.0, blank=True, null=True)
    pen_extra_km_charge = models.FloatField(default=0.0, blank=True, null=True)
    pen_extra_hours_charge = models.FloatField(default=0.0, blank=True, null=True)
    pen_no_of_pcs = models.IntegerField(default=0, blank=True)
    pen_weight = models.CharField(max_length=100, null=True, blank=True)
    pen_dimensions = models.CharField(max_length=200, null=True, blank=True)
    pen_cbm = models.CharField(max_length=100, null=True, blank=True)

    pen_pickup_contact_name = models.CharField(max_length=150, null=True, blank=True)
    pen_pickup_contact_mobile = models.CharField(max_length=20, null=True, blank=True)
    pen_delivery_contact_name = models.CharField(max_length=150, null=True, blank=True)
    pen_delivery_contact_mobile = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return str(self.pen_enquirynumber) if self.pen_enquirynumber else "N/A"
