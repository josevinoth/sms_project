from django.db import models
from ..models import RequirementsInfo,Busnotwon,GstexcemptionInfo,CustomertypeInfo,Salestatus,Calltype,Callnature,Callpurpose,Cusnewexist,Industrytype,Packreuqirementinfo,Supplyinfo,Transrequirementinfo,Whrequirementinfo,Location_info,CustomerInfo

class SalesInfo(models.Model):
    s_date_of_call = models.DateField(null = True,blank=True)
    s_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE,related_name='s_customer_name', db_column='s_customer_name', default='')
    s_customer_new_name = models.CharField(blank=True, null=True,max_length=30)
    s_customer_type = models.ForeignKey(CustomertypeInfo,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_customer_new = models.ForeignKey(Cusnewexist, on_delete=models.CASCADE, default='')
    s_industry_type = models.ForeignKey(Industrytype,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_requirement = models.ForeignKey(RequirementsInfo,blank=True, null=True,on_delete=models.CASCADE, default='')
    s_wh_requirement = models.ForeignKey(Whrequirementinfo,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_trans_requirement = models.ForeignKey(Transrequirementinfo,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_pack_requirement = models.ForeignKey(Packreuqirementinfo,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_fac_mgmt_requirement = models.ForeignKey(CustomerInfo,blank=True, null=True, on_delete=models.CASCADE, related_name='s_fac_mgmt_requirement', db_column='s_fac_mgmt_requirement',default='')
    s_manpower_requirement = models.ForeignKey(CustomerInfo,blank=True, null=True, on_delete=models.CASCADE,related_name='s_manpower_requirement', db_column='s_manpower_requirement' ,default='')
    s_supply_type = models.ForeignKey(Supplyinfo,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_location = models.ForeignKey(Location_info,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_call_type = models.ForeignKey(Calltype,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_call_nature = models.ForeignKey(Callnature,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_call_purpose = models.ForeignKey(Callpurpose,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_Person_name = models.CharField(blank=True, null=True,max_length=30)
    s_department = models.CharField(blank=True, null=True,max_length=30)
    s_designation = models.CharField(blank=True, null=True,max_length=30)
    s_contact_no = models.CharField(blank=True, null=True,max_length=30)
    s_email_id = models.CharField(blank=True, null=True,max_length=30)
    s_decision_maker = models.ForeignKey(GstexcemptionInfo,blank=True, null=True, on_delete=models.CASCADE,related_name='s_decision_maker', db_column='s_decision_maker', default='')
    s_name_desg_dm = models.CharField(blank=True, null=True,max_length=30)
    s_joint_call_name = models.CharField(blank=True, null=True,max_length=30)
    s_vol_bus_customer = models.CharField(blank=True, null=True,max_length=30)
    s_customer_prospective = models.ForeignKey(GstexcemptionInfo,blank=True, null=True, on_delete=models.CASCADE, related_name='s_customer_prospective', db_column='s_customer_prospective',default='')
    s_noreason_cp = models.CharField(blank=True, null=True,max_length=30)
    s_yesdate_quote = models.DateField(null = True,blank=True)
    s_quote_ref = models.CharField(blank=True, null=True,max_length=30)
    s_bus_won_not = models.ForeignKey(GstexcemptionInfo,blank=True, null=True, on_delete=models.CASCADE,related_name='s_bus_won_not', db_column='s_bus_won_not', default='')
    s_not_reason = models.ForeignKey(Busnotwon, blank=True, null=True,on_delete=models.CASCADE, default='')
    s_yesdate_business = models.DateField(null = True,blank=True)
    s_kyc = models.ForeignKey(GstexcemptionInfo,blank=True, null=True, on_delete=models.CASCADE,related_name='s_kyc', db_column='s_kyc' ,default='')
    s_contract = models.ForeignKey(GstexcemptionInfo,blank=True, null=True, on_delete=models.CASCADE,related_name='s_contract', db_column='s_contract', default='')
    s_rate_approval = models.ForeignKey(GstexcemptionInfo, blank=True, null=True,on_delete=models.CASCADE,related_name='s_rate_approval', db_column='s_rate_approval', default='')
    s_expected_prof = models.CharField(blank=True, null=True,max_length=30)
    s_approver_name = models.ForeignKey(GstexcemptionInfo,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_status = models.ForeignKey(Salestatus,blank=True, null=True, on_delete=models.CASCADE, default='')
    s_remark = models.TextField(blank=True, null=True)
    s_next_meet_schd_date = models.DateField(null = True,blank=True)
    s_meet_cancel_remark = models.CharField(blank=True, null=True,max_length=30)
    s_credit_period = models.CharField(blank=True, null=True,max_length=30)
    s_complain_complement = models.CharField(blank=True, null=True,max_length=30)
    s_minutes_of_meet = models.CharField(blank=True, null=True,max_length=30)
    s_Test = models.CharField(blank=True, null=True,max_length=30)

    def __str__(self):
        return self.s_customer_name