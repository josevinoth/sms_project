from django.db import models
from ..models import Prespectivec_customer_NoInfo,MyUser,Business_won_NoInfo,faciltiyrequirementinfo,Busnotwon,YesNoInfo,CustomertypeInfo,Salestatus,Calltype,Callnature,Callpurpose,Cusnewexist,Industrytype,Packreuqirementinfo,Supplyinfo,Transrequirementinfo,Whrequirementinfo,Location_info,CustomerInfo

def sales_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'Sales_Files/{0}/{1}'.format(instance.s_sale_number, filename)
class SalesInfo(models.Model):
    s_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE,related_name='s_customer_name', db_column='s_customer_name', blank=True, null=True)
    s_customer_new_name = models.CharField(blank=True, null=True,max_length=50)
    s_customer_type = models.ForeignKey(CustomertypeInfo,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_customer_new = models.ForeignKey(Cusnewexist, on_delete=models.CASCADE, default='')
    s_industry_type = models.ForeignKey(Industrytype,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_wh_requirement = models.ForeignKey(Whrequirementinfo,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_trans_requirement = models.ForeignKey(Transrequirementinfo,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_pack_requirement = models.ForeignKey(Packreuqirementinfo,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_fac_mgmt_requirement = models.ForeignKey(faciltiyrequirementinfo,blank=True, null=True, on_delete=models.CASCADE, related_name='s_fac_mgmt_requirement', db_column='s_fac_mgmt_requirement',default='')
    s_manpower_requirement = models.CharField(blank=True, null=True,max_length=30)
    s_supply_type = models.ForeignKey(Supplyinfo,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_location = models.ForeignKey(Location_info,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_Person_name = models.CharField(max_length=50)
    s_department = models.CharField(max_length=50)
    s_designation = models.CharField(max_length=50)
    s_contact_no = models.CharField(max_length=10)
    s_email_id = models.EmailField(max_length=100,default='')
    s_decision_maker = models.ForeignKey(YesNoInfo, on_delete=models.CASCADE,related_name='s_decision_maker', db_column='s_decision_maker', default='')
    s_name_dm = models.CharField(max_length=100)
    s_designation_dm = models.CharField(max_length=100,default='')
    s_emailid_dm = models.EmailField(max_length=100,default='')
    s_joint_call_name = models.CharField(blank=True, null=True,max_length=100)
    s_vol_customer = models.CharField(blank=True, null=True,max_length=30)
    s_bus_customer = models.CharField(blank=True, null=True,max_length=30)
    s_customer_prospective = models.ForeignKey(YesNoInfo,blank=True, null=True, on_delete=models.CASCADE, related_name='s_customer_prospective', db_column='s_customer_prospective',default=2)
    s_noreason_cp = models.ForeignKey(Prespectivec_customer_NoInfo,blank=True, null=True, on_delete=models.CASCADE,default=4)
    s_yesdate_quote = models.DateField(null = True,blank=True)
    s_quote_ref = models.CharField(blank=True, null=True,max_length=50)
    s_bus_won_not = models.ForeignKey(YesNoInfo,blank=True, null=True, on_delete=models.CASCADE,related_name='s_bus_won_not', db_column='s_bus_won_not', default=2)
    s_not_reason = models.ForeignKey(Business_won_NoInfo,blank=True, null=True, on_delete=models.CASCADE,default=4)
    s_yesdate_business = models.DateField(null = True,blank=True)
    s_kyc = models.ForeignKey(YesNoInfo,blank=True, null=True, on_delete=models.CASCADE,related_name='s_kyc', db_column='s_kyc' ,default=2)
    s_contract = models.ForeignKey(YesNoInfo,blank=True, null=True, on_delete=models.CASCADE,related_name='s_contract', db_column='s_contract', default=2)
    s_rate_approval = models.ForeignKey(YesNoInfo,blank=True, null=True, related_name='s_rate_approval', db_column='s_rate_approval',on_delete=models.CASCADE, default=2)
    s_expected_prof = models.IntegerField(blank=True, null=True)
    s_approver_name = models.ForeignKey(MyUser, related_name='s_approver_name', db_column='s_approver_name',on_delete=models.CASCADE, blank=True, null=True,default=2)
    s_status = models.ForeignKey(Salestatus,blank=True, null=True, on_delete=models.CASCADE, default=1)
    s_next_meet_schd_date = models.DateField(null = True,blank=True)
    s_credit_period = models.IntegerField(blank=True, null=True)
    s_created_at = models.DateTimeField(null=True, auto_now_add=True)
    s_updated_at = models.DateTimeField(null=True, auto_now=True)
    s_updated_by = models.ForeignKey(MyUser, related_name='s_updated_by', db_column='s_updated_by',on_delete=models.CASCADE, null=True)
    s_created_by = models.ForeignKey(MyUser, related_name='s_created_by', db_column='s_created_by',on_delete=models.CASCADE, blank=True, null=True)
    s_business_start_days=models.IntegerField(null = True,blank=True,default=0)
    s_sale_number = models.CharField(blank=True, null=True,max_length=30)
    s_attachment = models.FileField(upload_to=sales_directory_path, null=True, blank=True)
    class Meta:
        ordering = ["s_sale_number"]
    def __str__(self):
        return self.s_sale_number