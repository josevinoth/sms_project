from django.contrib import admin
from django.contrib.auth.models import User
from .models import faciltiyrequirementinfo,manpowerrequirementinfo,CustomerInfo,CustomertypeInfo,Busnotwon,Salestatus,Callpurpose,Callnature,Calltype,Supplyinfo,Packreuqirementinfo,Transrequirementinfo,Whrequirementinfo,Industrytype,RequirementsInfo,Cusnewexist,servicetype_info,ExpenseTypeInfo,ExpenseUOMInfo,Fumigation_ActionInfo,Department_info,RoleInfo,PaymentcycleInfo,StatusList,Country,State,City,Check_in_out,GstexcemptionInfo,UOM,Received_not,UploadInfo,DamagereportInfo,ActiveinactiveInfo,StackingInfo,Wh_chargetype

# Register your models here.
admin.site.register(StatusList)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(RoleInfo)
admin.site.register(Department_info)
admin.site.register(Check_in_out)
admin.site.register(GstexcemptionInfo)
admin.site.register(UOM)
admin.site.register(Received_not)
admin.site.register(UploadInfo)
admin.site.register(DamagereportInfo)
admin.site.register(ActiveinactiveInfo)
admin.site.register(StackingInfo)
admin.site.register(Wh_chargetype)
admin.site.register(PaymentcycleInfo)
admin.site.register(Fumigation_ActionInfo)
admin.site.register(ExpenseTypeInfo)
admin.site.register(ExpenseUOMInfo)
admin.site.register(servicetype_info)
admin.site.register(RequirementsInfo)
admin.site.register(Cusnewexist)
admin.site.register(Industrytype)
admin.site.register(Whrequirementinfo)
admin.site.register(Transrequirementinfo)
admin.site.register(Packreuqirementinfo)
admin.site.register(Supplyinfo)
admin.site.register(Calltype)
admin.site.register(Callnature)
admin.site.register(Callpurpose)
admin.site.register(Salestatus)
admin.site.register(Busnotwon)
admin.site.register(CustomertypeInfo)
admin.site.register(CustomerInfo)
admin.site.register(manpowerrequirementinfo)
admin.site.register(faciltiyrequirementinfo)



