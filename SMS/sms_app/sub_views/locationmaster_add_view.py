import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from ..forms import LocationmasteraddForm
from ..models import LocationmasterInfo,CustomerInfo,TrbusinesstypeInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def locationmaster_add(request,locationmaster_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if locationmaster_id == 0:
            con_val = request.GET.get('lm_concatenate')
            print(con_val)
            print('Inside Get')
            lm_record_count = LocationmasterInfo.objects.filter(lm_concatenate=con_val).count()
            print("Record Count", lm_record_count)
            if lm_record_count == 1:
                print('Inside GET first loop')
                print('Record Exist')
                messages.info(request, 'Record Exist')
                return redirect(request.META['HTTP_REFERER'])
            else:
                print('Inside GET second loop')
                form = LocationmasteraddForm()
        else:
            print('Inside Get Else')
            locationmaster=LocationmasterInfo.objects.get(pk=locationmaster_id)
            form = LocationmasteraddForm(instance=locationmaster)
        return render(request, "asset_mgt_app/locationmaster_add.html", {'form': form,'first_name': first_name})
    else:
        if locationmaster_id == 0:
            con_val = request.POST.get('lm_concatenate')
            print(con_val)
            print('Inside Post')
            lm_record_count=LocationmasterInfo.objects.filter(lm_concatenate=con_val).count()
            print("Record Count",lm_record_count)
            if lm_record_count==1:
                print('Inside Post first loop')
                print('Record Exist')
                messages.info(request, 'Record Exist')
                return redirect(request.META['HTTP_REFERER'])
            else:
                print('Inside Post second loop')
                form = LocationmasteraddForm(request.POST)
                if form.is_valid():
                    form.save()
                return redirect('/SMS/locationmaster_list')
        else:
            print('Inside Post Else')
            con_val = request.POST.get('lm_concatenate')
            print(con_val)
            # con_val = LocationmasterInfo.objects.get(pk=locationmaster_id).lm_concatenate
            # if form.is_valid():
            #     form.save()
            lm_record_count = LocationmasterInfo.objects.filter(lm_concatenate=con_val).count()
            print("Record Count",lm_record_count)
            if lm_record_count>1:
                print('Inside Post Else first loop')
                print('Record Exist')
                messages.info(request, 'Record Exist')
                return redirect(request.META['HTTP_REFERER'])
            else:
                print('Inside Post Else Second loop')
                locationmaster = LocationmasterInfo.objects.get(pk=locationmaster_id)
                form = LocationmasteraddForm(request.POST, instance=locationmaster)
                if form.is_valid():
                    form.save()
            return redirect('/SMS/locationmaster_list')

# List locationmaster
@login_required(login_url='login_page')
def locationmaster_list(request):
    first_name = request.session.get('first_name')
    context = {'locationmaster_list' : LocationmasterInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/locationmaster_list.html",context)

#Delete locationmaster
@login_required(login_url='login_page')
def locationmaster_delete(request,locationmaster_id):
    locationmaster = LocationmasterInfo.objects.get(pk=locationmaster_id)
    locationmaster.delete()
    return redirect('/SMS/locationmaster_list')

#Get Customer Model
@login_required(login_url='login_page')
def load_customer_model(request):
    unit_list=[]
    unit_name=[]
    unit_name_list = []
    lm_customer_name_id = request.GET.get('lm_customer_name_id')
    print("Customer Model ID",lm_customer_name_id)
    customer_businessmodel = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_businessmodel')
    print("customer_businessmodel",customer_businessmodel)
    customer_businessmodel_val=customer_businessmodel[0]['cu_businessmodel'] #Get value from Queryset
    print(customer_businessmodel_val)
    lm_customer_model_id=TrbusinesstypeInfo.objects.filter(id=customer_businessmodel_val).values('tb_trbusinesstype')
    print("customer_businessmodel_id", lm_customer_model_id)
    customer_businessmodel_txt= lm_customer_model_id[0]['tb_trbusinesstype']  # Get value from Queryset
    print(customer_businessmodel_txt)
    data = {
        'customer_businessmodel_txt':customer_businessmodel_txt
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))