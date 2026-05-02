from django.db import models
from .my_user_mod import MyUser
from .location_info_mod import Location_info
from .enquiry_source_mod import Enquiry_source
from .customer_mod import CustomerInfo
from .wh_requirement_mod import Whrequirementinfo
from .pack_requirement_mod import Packreuqirementinfo
from .tours_requirement_mod import Toursrequirementinfo
from .express_info_mod import Express_info
from .trans_info_mod import Trans_info
from .support_info_mod import Support_info
from .shipment_type_mod import Shipment_type
from .delivery_type_mod import Delivery_type
from .travel_type_mod import Travel_type

import os

def sale_enquiry_path(instance, filename):
    # This will upload to MEDIA_ROOT/SaleEnquiryAttachments/<enquiry_id>/<filename>
    return os.path.join('SaleEnquiryAttachments', str(instance.enquiry_id), filename)

class SaleEnquiry(models.Model):
    enquiry_id = models.CharField(max_length=100, default='', blank=True, null=True)
    enquiry_date_time = models.DateTimeField(null=True, blank=True)
    enquiry_source = models.ForeignKey(Enquiry_source, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, null=True, blank=True)
    new_customer_name = models.CharField(max_length=200, default='', blank=True, null=True)
    customer_code = models.CharField(max_length=100, default='', blank=True, null=True)
    contact_person_name = models.CharField(max_length=100, default='', blank=True, null=True)
    contact_no = models.CharField(max_length=20, default='', blank=True, null=True)
    mail = models.EmailField(max_length=100, default='', blank=True, null=True)
    address = models.TextField(default='', blank=True, null=True)
    service_type = models.CharField(max_length=100, default='', blank=True, null=True)

    # Warehouse Fields
    wh_customer_type = models.ForeignKey(Whrequirementinfo, on_delete=models.CASCADE, null=True, blank=True)
    wh_sqft_req = models.IntegerField(blank=True, null=True)
    wh_scope_of_lul = models.CharField(max_length=100, default='', blank=True, null=True)
    wh_tonnage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    wh_no_of_months_req = models.IntegerField(blank=True, null=True)
    wh_rfq_closed_date = models.DateField(blank=True, null=True)

    # Transport Fields
    tr_customer_type = models.ForeignKey(Trans_info, on_delete=models.CASCADE, null=True, blank=True)
    tr_no_of_vehicles_req = models.IntegerField(blank=True, null=True)
    tr_veh_type_req = models.CharField(max_length=100, default='', blank=True, null=True)
    tr_from = models.CharField(max_length=100, default='', blank=True, null=True)
    tr_to = models.CharField(max_length=100, default='', blank=True, null=True)
    tr_rfq_closed_date = models.DateField(blank=True, null=True)
    tr_no_of_avg_trips_per_month = models.IntegerField(blank=True, null=True)
    tr_tonnage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Packing Fields
    pa_customer_type = models.ForeignKey(Packreuqirementinfo, on_delete=models.CASCADE, null=True, blank=True)
    pa_inhouse_onsite = models.CharField(max_length=100, default='', blank=True, null=True)
    pa_lul_scope = models.CharField(max_length=100, default='', blank=True, null=True)
    pa_transport_scope = models.CharField(max_length=100, default='', blank=True, null=True)
    pa_no_of_boxes_per_month = models.IntegerField(blank=True, null=True)
    pa_rfq_closed_date = models.DateField(blank=True, null=True)

    # Express Fields
    ex_customer_type = models.ForeignKey(Express_info, on_delete=models.CASCADE, null=True, blank=True)
    ex_veh_type = models.CharField(max_length=100, default='', blank=True, null=True)
    ex_no_of_vehicles = models.IntegerField(blank=True, null=True)
    ex_pickup = models.CharField(max_length=100, default='', blank=True, null=True)
    ex_delivery = models.CharField(max_length=100, default='', blank=True, null=True)
    ex_shipment_type = models.ForeignKey(Shipment_type, on_delete=models.CASCADE, null=True, blank=True)
    ex_no_of_shipments = models.IntegerField(blank=True, null=True)
    ex_avg_weight_per_shipment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ex_delivery_type = models.ForeignKey(Delivery_type, on_delete=models.CASCADE, null=True, blank=True)
    ex_rfq_closed_date = models.DateField(blank=True, null=True)

    # Support Fields
    su_customer_type = models.ForeignKey(Support_info, on_delete=models.CASCADE, null=True, blank=True)
    su_no_of_manpowers = models.IntegerField(blank=True, null=True)
    su_shift_type = models.CharField(max_length=100, default='', blank=True, null=True)
    su_working_days = models.CharField(max_length=100, default='', blank=True, null=True)
    su_supervisors = models.IntegerField(blank=True, null=True)
    su_loaders = models.IntegerField(blank=True, null=True)
    su_rfq_closed_date = models.DateField(blank=True, null=True)

    # MC Fields
    mc_customer_type = models.ForeignKey(Toursrequirementinfo, on_delete=models.CASCADE, null=True, blank=True)
    mc_travel_type = models.ForeignKey(Travel_type, on_delete=models.CASCADE, null=True, blank=True)
    mc_from = models.CharField(max_length=100, default='', blank=True, null=True)
    mc_to = models.CharField(max_length=100, default='', blank=True, null=True)
    mc_no_of_passengers = models.IntegerField(blank=True, null=True)
    mc_travel_date = models.DateField(blank=True, null=True)
    mc_return_date = models.DateField(blank=True, null=True)
    mc_vehicle_type = models.CharField(max_length=100, default='', blank=True, null=True)
    mc_package_req = models.CharField(max_length=100, default='', blank=True, null=True)
    mc_hotel_req = models.CharField(max_length=100, default='', blank=True, null=True)
    mc_rfq_closed_date = models.DateField(blank=True, null=True)

    wh_attachment = models.FileField(upload_to=sale_enquiry_path, null=True, blank=True)
    tr_attachment = models.FileField(upload_to=sale_enquiry_path, null=True, blank=True)
    pa_attachment = models.FileField(upload_to=sale_enquiry_path, null=True, blank=True)
    ex_attachment = models.FileField(upload_to=sale_enquiry_path, null=True, blank=True)
    su_attachment = models.FileField(upload_to=sale_enquiry_path, null=True, blank=True)
    mc_attachment = models.FileField(upload_to=sale_enquiry_path, null=True, blank=True)

    created_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, related_name='saleenquiry_created_by')
    updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, related_name='saleenquiry_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def get_product_names(self):
        products = []
        if self.wh_customer_type:
            products.append("Warehouse")
        if self.tr_customer_type:
            products.append("Transport")
        if self.pa_customer_type:
            products.append("Packing")
        if self.ex_customer_type:
            products.append("Express")
        if self.su_customer_type:
            products.append("Support")
        if self.mc_customer_type:
            products.append("MC Tours&Travels")
        return ", ".join(products)

    def __str__(self):
        return self.enquiry_id or str(self.id)
