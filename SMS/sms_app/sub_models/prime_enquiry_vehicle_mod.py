from django.db import models
from .prime_enquirynote_mod import PrimeEnquirynoteInfo
from ..models import MyUser, VehicletypeInfo, VehiclecategoryInfo


class PrimeEnquiryVehicle(models.Model):
    """
    Stores vehicle detail rows for Prime business type enquiry notes.
    Similar in structure to Enquirynotevehicle but isolated for the Prime flow.
    """
    pev_enquirynumber = models.ForeignKey(
        PrimeEnquirynoteInfo,
        on_delete=models.PROTECT,
        default='',
        related_name='prime_vehicles'
    )
    pev_vehicletype = models.ForeignKey(
        VehicletypeInfo,
        on_delete=models.CASCADE,
        default='',
        null=True, blank=True
    )
    pev_vehiclecategory = models.ForeignKey(
        VehiclecategoryInfo,
        on_delete=models.CASCADE,
        default='',
        null=True, blank=True
    )
    pev_quantity = models.IntegerField(blank=True, null=True, default=0)
    pev_created_at = models.DateTimeField(null=True, auto_now_add=True)
    pev_updated_at = models.DateTimeField(null=True, auto_now=True)
    pev_updated_by = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='pev_updated_by',
        db_column='pev_updated_by',
        null=True
    )

    class Meta:
        ordering = ['pev_enquirynumber']

    def __str__(self):
        return str(self.pev_enquirynumber) if self.pev_enquirynumber else 'N/A'

    @property
    def get_allotment(self):
        return self.primevehicleallotmentinfo_set.first()

    @property
    def allotted_count(self):
        return self.primevehicleallotmentinfo_set.count()

    @property
    def is_allotment_complete(self):
        qty = self.pev_quantity or 0
        if qty <= 0:
            return False
        return self.allotted_count >= qty
