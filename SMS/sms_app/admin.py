from django.contrib import admin
from django.contrib.auth.models import User
from .models import ExpenseTypeInfo,ExpenseUOMInfo,Fumigation_ActionInfo,Department_info,RoleInfo,PaymentcycleInfo,StatusList,Country,State,City,Check_in_out,GstexcemptionInfo,UOM,Received_not,UploadInfo,DamagereportInfo,ActiveinactiveInfo,StackingInfo,Wh_chargetype

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




