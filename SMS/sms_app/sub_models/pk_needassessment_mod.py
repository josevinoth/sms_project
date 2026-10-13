from django.db import models
from ..models import StatusList, MyUser,Packreuqirementinfo, Natypeofwork, Nadeliverytype, Naspecialrequirements, Napackingfield, CustomerInfo, Nawoodtreatmentreq, Nabvmcustomer, Nawoodnorms, VehicletypeInfo, Natypeofaccess, Stockdescription

# Function to handle file upload path
def Pkneedassessment_directory_path(instance, filename):
    return 'Pkneedassessmentfiles/{0}/{1}'.format(instance.na_assessment_num, filename)


class PkneedassessmentInfo(models.Model):
    na_assessment_num = models.CharField(max_length=100, null=True, blank=True, default='')
    na_date = models.DateField(blank=True, null=True)
    na_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, default='')
    na_type_of_work = models.ForeignKey(Natypeofwork, on_delete=models.CASCADE, default='')
    na_type_of_pack1 = models.ForeignKey(Packreuqirementinfo, on_delete=models.CASCADE, null=True, blank=True)
    # Updated field to ManyToMany for multi-select functionality
    na_wood_treatment_req = models.ManyToManyField(Nawoodtreatmentreq, blank=True)
    na_unloading = models.ForeignKey(Nabvmcustomer, on_delete=models.CASCADE, related_name='na_unloading', db_column='na_unloading', default='')
    na_wood_norms = models.ManyToManyField(Nawoodnorms,blank=True)
    na_delivery_by = models.ForeignKey(Nabvmcustomer, on_delete=models.CASCADE, related_name='na_delivery_by', db_column='na_delivery_by', null=True, blank=True, default='')
    na_vehicle_type = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='',null=True,blank=True)

    # Updated field to ManyToMany for multi-select functionality
    na_type_of_access = models.ManyToManyField(Natypeofaccess,blank=True)

    na_created_at = models.DateTimeField(null=True, auto_now_add=True)
    na_updated_at = models.DateTimeField(null=True, auto_now=True)
    na_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='na_updated_by', db_column='na_updated_by', null=True)
    na_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6, blank=True, null=True)
    na_attach = models.FileField(upload_to=Pkneedassessment_directory_path, null=True, blank=True)
    na_others_type_pack = models.CharField(max_length=100, null=True, blank=True, default='')
    na_delivery_type = models.ForeignKey(Nadeliverytype, on_delete=models.CASCADE, blank=True, null=True, default='')
    na_packing_field = models.ForeignKey(Napackingfield, on_delete=models.CASCADE, blank=True, null=True, default='')
    na_special_requirements = models.ManyToManyField(Naspecialrequirements,blank=True)
    na_special_requirements_details = models.TextField(blank=True, null=True)
    na_delivery_location = models.CharField(max_length=100, null=True, blank=True, default='')
    na_customer_new_name = models.CharField(blank=True, null=True, max_length=500)
    na_contactno = models.CharField(max_length=10, default='',null=True)
    na_email = models.EmailField(max_length=50, default='')
    na_client_scope = models.TextField(blank=True, null=True)
    na_bvm_scope = models.TextField(blank=True, null=True)
    na_sales_person = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ["na_assessment_num"]

    def __str__(self):
        return str(self.na_assessment_num) if self.na_assessment_num else "N/A"

    @property
    def access_types_str(self):
        return " ".join([str(a.type_of_access).upper() for a in self.na_type_of_access.all()]) if self.pk else ""

    @property
    def wood_norms_str(self):
        return " ".join([str(n.wood_norms).upper() for n in self.na_wood_norms.all()]) if self.pk else ""

    @property
    def is_ht_selected(self):
        if not self.pk:
            return False
        for t in self.na_wood_treatment_req.all():
            name = str(t.wood_treatment_req).upper()
            if 'HT' in name or 'HEAT' in name:
                return True
        return False

    @property
    def is_fumigation_selected(self):
        if not self.pk:
            return False
        for t in self.na_wood_treatment_req.all():
            name = str(t.wood_treatment_req).upper()
            if 'FUMIG' in name:
                return True
        return False

    @property
    def air_crack_norm(self):
        if not self.pk:
            return ""
        for n in self.na_wood_norms.all():
            if 'AIR' in n.wood_norms.upper():
                return n.wood_norms
        return ""

    @property
    def notches_norm(self):
        if not self.pk:
            return ""
        for n in self.na_wood_norms.all():
            if 'NOTCH' in n.wood_norms.upper():
                return n.wood_norms
        return ""

    @property
    def fungus_norm(self):
        if not self.pk:
            return ""
        for n in self.na_wood_norms.all():
            if 'FUNG' in n.wood_norms.upper():
                return n.wood_norms
        return ""

    @property
    def tolerance_norm(self):
        if not self.pk:
            return ""
        for n in self.na_wood_norms.all():
            if 'TOLERANCE' in n.wood_norms.upper():
                return n.wood_norms
        return ""

    @property
    def barks_norm(self):
        if not self.pk:
            return ""
        for n in self.na_wood_norms.all():
            if 'BARK' in n.wood_norms.upper():
                return n.wood_norms
        return ""

    @property
    def all_wood_norms_display(self):
        return ", ".join([str(n.wood_norms) for n in self.na_wood_norms.all()]) if self.pk else ""


def na_attachment_directory_path(instance, filename):
    na_identifier = instance.na.na_assessment_num if instance.na and instance.na.na_assessment_num else 'common'
    return 'Pkneedassessmentfiles/{0}/{1}'.format(na_identifier, filename)


class PkneedassessmentAttachmentInfo(models.Model):
    na = models.ForeignKey(PkneedassessmentInfo, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=na_attachment_directory_path)
    filename = models.CharField(max_length=300, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"NA {self.na.na_assessment_num} - {self.filename or self.file.name}"
