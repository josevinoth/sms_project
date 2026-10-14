from django.db import models
from .customer_mod import CustomerInfo
from .customerdepartment_mod import CustomerdepartmentInfo
from .my_user_mod import MyUser


class DmrTemplateMaster(models.Model):
    template_name = models.CharField(max_length=200, help_text="Template Name, e.g., 'EIPL Standard Sea Export'")
    customer = models.ForeignKey(
        CustomerInfo, on_delete=models.CASCADE, null=True, blank=True,
        related_name="dmr_templates", help_text="Associated customer (leave blank for generic default)"
    )
    department = models.ForeignKey(
        CustomerdepartmentInfo, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="dmr_templates", help_text="Associated department (leave blank for all departments of this customer)"
    )
    description = models.TextField(blank=True, null=True, help_text="Optional description or customer notes")
    is_active = models.BooleanField(default=True, help_text="Whether this template is currently active")
    is_default = models.BooleanField(default=False, help_text="Set as fallback default template")
    merge_identical_cells = models.BooleanField(
        default=False,
        help_text="Enable cell merging on identical Job/LR rows (e.g., EIPL style report)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "dmr_template_master"
        ordering = ["template_name"]

    def __str__(self):
        cust = self.customer.cu_name if self.customer else "Generic / All Customers"
        dept = f" ({self.department.ct_customerdepartment})" if self.department else ""
        return f"{self.template_name} - {cust}{dept}"


class DmrTemplateColumn(models.Model):
    PAGE_CHOICES = [
        ('ENQUIRY', 'Enquiry / Indent Page'),
        ('CONSIGNMENT', 'Consignment & Goods Page'),
        ('ALLOTMENT', 'Vehicle Allotment Page'),
        ('TRIP_LOADING', 'Dispatch & Loading Page'),
        ('TRIP_UNLOADING', 'Unloading & Delivery Page'),
        ('CHARGES_FINANCE', 'Charges & Finance Page'),
        ('SYSTEM', 'System / Calculated / Custom'),
    ]

    template = models.ForeignKey(
        DmrTemplateMaster, on_delete=models.CASCADE, related_name="columns"
    )
    column_order = models.PositiveIntegerField(default=1, help_text="1-based position in Excel")
    column_header = models.CharField(max_length=255, help_text="Display title in Excel header row")
    source_page = models.CharField(max_length=50, choices=PAGE_CHOICES, default='SYSTEM')
    field_key = models.CharField(
        max_length=100,
        help_text="Key mapping to field catalog (e.g. 'co_consignmentnumber', 'total_charges', etc.)"
    )
    date_format = models.CharField(
        max_length=50, blank=True, null=True, default="",
        help_text="Optional format string (e.g. '%d-%m-%Y', '%H:%M', '%d-%m-%Y %H:%M', '%B')"
    )
    # Multi-charge summation support for total charges / custom charges:
    included_charges = models.CharField(
        max_length=500, blank=True, null=True, default="",
        help_text="Comma-separated charge keys to sum for total cost columns (e.g. 'tripcost,halting,toll,parking,unloading')"
    )
    static_value = models.CharField(
        max_length=255, blank=True, null=True, default="",
        help_text="Static text value if field_key is 'static_text'"
    )
    column_width = models.PositiveIntegerField(
        default=15, help_text="Excel column width in characters"
    )

    class Meta:
        db_table = "dmr_template_column"
        ordering = ["template", "column_order"]

    def __str__(self):
        return f"[{self.column_order}] {self.column_header} ({self.field_key})"
