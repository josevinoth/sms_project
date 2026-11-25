from django.db import models
from ..models import (
    PkneedassessmentInfo, PkpurchaseorderInfo, CustomerInfo, MyUser, POdimension, PkcostingsummaryInfo
)


class PkInvoice(models.Model):
    """
    PMS Invoice — Master record.
    Supports multiple jobs for one customer, created BEFORE Gate Pass is issued.
    """
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Partial', 'Partial'),
        ('Paid', 'Paid'),
    ]

    inv_number = models.CharField(max_length=50, unique=True, verbose_name="Invoice Number")
    inv_job_no = models.CharField(max_length=255, blank=True, null=True, verbose_name="Job No(s)")
    inv_assessment_num = models.ForeignKey(
        PkneedassessmentInfo, on_delete=models.CASCADE,
        blank=True, null=True, verbose_name="Assessment"
    )
    inv_customer_po = models.ForeignKey(
        PkpurchaseorderInfo, on_delete=models.CASCADE,
        blank=True, null=True, verbose_name="Customer PO"
    )
    inv_customer_name = models.ForeignKey(
        CustomerInfo, on_delete=models.CASCADE,
        blank=True, null=True, verbose_name="Customer"
    )
    inv_customer_state = models.CharField(max_length=100, blank=True, null=True, verbose_name="State")
    inv_customer_pincode = models.CharField(max_length=20, blank=True, null=True, verbose_name="Pincode")
    inv_customer_gstin = models.CharField(max_length=50, blank=True, null=True, verbose_name="GSTIN")

    inv_date = models.DateField(verbose_name="Invoice Date")
    inv_base_amount = models.FloatField(default=0.0, verbose_name="Base Amount (₹)")
    inv_gst_rate = models.FloatField(default=18.0, verbose_name="GST Rate (%)")
    inv_cgst_amount = models.FloatField(default=0.0, verbose_name="CGST (₹)")
    inv_sgst_amount = models.FloatField(default=0.0, verbose_name="SGST (₹)")
    inv_igst_amount = models.FloatField(default=0.0, verbose_name="IGST (₹)")
    inv_total_amount = models.FloatField(default=0.0, verbose_name="Grand Total (₹)")
    inv_remarks = models.TextField(blank=True, null=True, verbose_name="Remarks")
    inv_payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES,
        default='Pending', verbose_name="Payment Status"
    )
    inv_created_by = models.ForeignKey(
        MyUser, on_delete=models.SET_NULL, null=True,
        related_name='pk_invoices_created', verbose_name="Created By"
    )
    inv_created_at = models.DateTimeField(auto_now_add=True)
    inv_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.inv_number


class PkInvoiceItem(models.Model):
    """
    PMS Invoice Line Item — can represent a Job or PO Dimension.
    Carries PMS Tally categorization and revenue charge breakdown.
    """
    PRIMARY_COST_CATEGORY_CHOICES = [
        ('Packing Charges', 'Packing Charges'),
        ('Packing Charges Service', 'Packing Charges Service'),
        ('Supply of Packing Material', 'Supply of Packing Material'),
        ('Forklift Handling Charges', 'Forklift Handling Charges'),
        ('Freight Charges', 'Freight Charges'),
        ('Handling Charges', 'Handling Charges'),
        ('Loading Charges', 'Loading Charges'),
        ('Unloading Charges', 'Unloading Charges'),
        ('Repacking Charges', 'Repacking Charges'),
    ]

    TAX_TYPE_CHOICES = [
        ('18%', '18%'),
        ('GST-5%', 'GST-5%'),
        ('IGST 18%', 'IGST 18%'),
        ('LUT', 'LUT'),
        ('Nil tax', 'Nil tax'),
        ('SEZ', 'SEZ'),
    ]

    inv_master = models.ForeignKey(
        PkInvoice, on_delete=models.CASCADE,
        related_name='items', verbose_name="Invoice"
    )
    inv_costing_summary = models.ForeignKey(
        PkcostingsummaryInfo, on_delete=models.SET_NULL,
        blank=True, null=True, verbose_name="Costing Summary / Job"
    )
    inv_job_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="Job No")
    inv_job_date = models.DateField(blank=True, null=True, verbose_name="Job Date")
    inv_primary_cost_category = models.CharField(
        max_length=100, choices=PRIMARY_COST_CATEGORY_CHOICES,
        default='Packing Charges', verbose_name="Primary Cost Category"
    )
    inv_tax_type = models.CharField(
        max_length=50, choices=TAX_TYPE_CHOICES,
        default='18%', verbose_name="Tax Type"
    )

    inv_pod_dimension = models.ForeignKey(
        POdimension, on_delete=models.PROTECT,
        blank=True, null=True, verbose_name="PO Dimension"
    )
    # Snapshot fields
    inv_item_number = models.CharField(max_length=150, verbose_name="Item Number")
    inv_description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Description")
    inv_length = models.FloatField(default=0.0, verbose_name="Length")
    inv_width = models.FloatField(default=0.0, verbose_name="Width")
    inv_height = models.FloatField(default=0.0, verbose_name="Height")
    inv_uom = models.CharField(max_length=20, blank=True, null=True, verbose_name="UOM")
    inv_qty = models.IntegerField(default=1, verbose_name="Qty")
    inv_unit_value = models.FloatField(default=0.0, verbose_name="Unit Value (₹)")
    inv_total_value = models.FloatField(default=0.0, verbose_name="Total Value (₹)")

    # Charge Breakdown Ledgers (Matching Tally Columns R through AE)
    inv_handling_charges = models.FloatField(default=0.0, verbose_name="Handling Charges")
    inv_loading_charges = models.FloatField(default=0.0, verbose_name="Loading Charges")
    inv_unloading_charges = models.FloatField(default=0.0, verbose_name="Unloading Charges")
    inv_packing_charges_5 = models.FloatField(default=0.0, verbose_name="Packing Charges - 5%")
    inv_packing_charges_igst = models.FloatField(default=0.0, verbose_name="Packing Charges - IGST")
    inv_packing_charges_service = models.FloatField(default=0.0, verbose_name="Packing Charges - Service")
    inv_packing_charges_service_igst = models.FloatField(default=0.0, verbose_name="Packing Charges - Service - IGST")
    inv_packing_charges_service_sez = models.FloatField(default=0.0, verbose_name="Packing Charges - Service - SEZ")
    inv_packing_charges_sez = models.FloatField(default=0.0, verbose_name="Packing Charges - SEZ")
    inv_repacking_charges = models.FloatField(default=0.0, verbose_name="Repacking Charges")
    inv_repacking_charges_igst = models.FloatField(default=0.0, verbose_name="Repacking Charges - IGST")
    inv_scrap_wood = models.FloatField(default=0.0, verbose_name="Scrap Wood")
    inv_supply_packing_materials = models.FloatField(default=0.0, verbose_name="Supply of Packing Materials")
    inv_supply_packing_materials_igst = models.FloatField(default=0.0, verbose_name="Supply of Packing Materials - IGST")

    # Taxes (Tally Columns AF through AL)
    inv_cgst_9 = models.FloatField(default=0.0, verbose_name="CGST Output @ 9%")
    inv_sgst_9 = models.FloatField(default=0.0, verbose_name="SGST Output @ 9%")
    inv_cgst_6 = models.FloatField(default=0.0, verbose_name="CGST Output @ 6%")
    inv_sgst_6 = models.FloatField(default=0.0, verbose_name="SGST Output @ 6%")
    inv_cgst_2_5 = models.FloatField(default=0.0, verbose_name="CGST Output @ 2.5%")
    inv_sgst_2_5 = models.FloatField(default=0.0, verbose_name="SGST Output @ 2.5%")
    inv_igst = models.FloatField(default=0.0, verbose_name="IGST")
    inv_line_total = models.FloatField(default=0.0, verbose_name="Total Value")

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.inv_master.inv_number} — {self.inv_item_number} ({self.inv_job_no or ''})"
