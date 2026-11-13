from django.db import models
from .customer_mod import CustomerInfo
from .na_typeofreq_mod import Natypeofreq
from .pk_dimension_type_mod import Nadimensiontype
from .unit_of_measure_mod import Unitofmeasure
from .pk_stock_type_mod import Pkstocktype
from .pk_wood_description import Pkwooddescription
from .na_consumables_mod import Naconsumables
from .vehicletype_mod import VehicletypeInfo
from .my_user_mod import MyUser


class CustomerBoxItemMaster(models.Model):
    """Reusable customer-specific (or global) box/machine packaging specification master."""
    cbm_customer = models.ForeignKey(
        CustomerInfo, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='box_master_items'
    )
    cbm_bvm_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    cbm_item_code = models.CharField(max_length=120, default='', help_text='Customer Part Code / SKU / Drawing No')
    cbm_item_name = models.CharField(max_length=255, default='', help_text='Machine / Box Description')
    cbm_type_of_req = models.ForeignKey(Natypeofreq, on_delete=models.SET_NULL, null=True, blank=True)
    cbm_dimension_type = models.ForeignKey(Nadimensiontype, on_delete=models.SET_NULL, null=True, blank=True, default=4)
    cbm_length = models.FloatField(default=0.0)
    cbm_width = models.FloatField(default=0.0)
    cbm_height = models.FloatField(default=0.0)
    cbm_clearance = models.FloatField(default=0.0, null=True, blank=True)
    cbm_plywood_thickness = models.FloatField(default=0.0, null=True, blank=True)
    # Directional Clearance (cm): Length, Width, Top
    cbm_clr_length = models.FloatField(default=0.0)
    cbm_clr_width = models.FloatField(default=0.0)
    cbm_clr_top = models.FloatField(default=0.0)
    # Directional Thickness (cm): Length walls, Width walls, Height (Base + Top)
    cbm_thk_length = models.FloatField(default=7.0)
    cbm_thk_width = models.FloatField(default=7.0)
    cbm_thk_height = models.FloatField(default=20.0)
    cbm_uom = models.ForeignKey(Unitofmeasure, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'id__in': [1, 2, 3, 4]})
    cbm_job_weight = models.FloatField(default=0.0, help_text='Per job weight in KG')
    cbm_wood_type = models.ManyToManyField(Pkstocktype, blank=True)
    cbm_wood_description = models.ManyToManyField(Pkwooddescription, blank=True)
    cbm_consumables = models.ForeignKey(Naconsumables, on_delete=models.SET_NULL, null=True, blank=True)
    cbm_vechicle_type = models.ForeignKey(VehicletypeInfo, on_delete=models.SET_NULL, null=True, blank=True)
    cbm_notes = models.TextField(blank=True, null=True)
    cbm_is_active = models.BooleanField(default=True)
    cbm_created_at = models.DateTimeField(auto_now_add=True, null=True)
    cbm_updated_at = models.DateTimeField(auto_now=True, null=True)
    cbm_updated_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['cbm_customer__cu_name', 'cbm_item_code', 'cbm_item_name']

    def __str__(self):
        cust = self.cbm_customer.cu_name if self.cbm_customer else 'Global'
        code = self.cbm_item_code or self.cbm_bvm_code or ''
        return f"{cust} | {code} - {self.cbm_item_name}".strip(' -|')
