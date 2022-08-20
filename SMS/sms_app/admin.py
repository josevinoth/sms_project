from django.contrib import admin
from django.contrib.auth.models import User
from .models import StatusList,Country,State,City,Check_in_out,GstexcemptionInfo,UOM,Received_not,UploadInfo,DamagereportInfo,ActiveinactiveInfo,StackingInfo

# Register your models here.
admin.site.register(StatusList)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Check_in_out)
admin.site.register(GstexcemptionInfo)
admin.site.register(UOM)
admin.site.register(Received_not)
admin.site.register(UploadInfo)
admin.site.register(DamagereportInfo)
admin.site.register(ActiveinactiveInfo)
admin.site.register(StackingInfo)




