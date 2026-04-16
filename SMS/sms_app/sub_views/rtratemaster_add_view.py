from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..forms import RtratemasteraddForm
from ..models import RtratemasterInfo
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator

@login_required(login_url='login_page')
def rtratemaster_add(request,rtratemaster_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if rtratemaster_id == 0:
            form = RtratemasteraddForm()
        else:
            rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
            form = RtratemasteraddForm(instance=rtratemaster)
        return render(request, "asset_mgt_app/rtratemaster_add.html", {'form': form,'first_name': first_name,'user_id':user_id,})
    else:
        form = RtratemasteraddForm(request.POST)
        if form.is_valid():
            # Check for duplicates before saving
            ro_fromlocation = form.cleaned_data['ro_fromlocation']
            ro_tolocation = form.cleaned_data['ro_tolocation']
            ro_vehicletype = form.cleaned_data['ro_vehicletype']
            ro_customer = form.cleaned_data['ro_customer']
            ro_customerdepartment = form.cleaned_data['ro_customerdepartment']
            ro_vehiclecategory = form.cleaned_data['ro_vehiclecategory']
            ro_touchpoint = form.cleaned_data['ro_touchpoint']
            ro_touchpoint2 = form.cleaned_data['ro_touchpoint2']
            ro_touchpoint3 = form.cleaned_data['ro_touchpoint3']
            ro_touchpoint4 = form.cleaned_data['ro_touchpoint4']
            if not RtratemasterInfo.objects.filter(ro_fromlocation=ro_fromlocation,ro_tolocation=ro_tolocation,ro_vehicletype=ro_vehicletype,ro_customer=ro_customer,ro_customerdepartment=ro_customerdepartment,ro_vehiclecategory=ro_vehiclecategory,ro_touchpoint=ro_touchpoint,ro_touchpoint2=ro_touchpoint2,ro_touchpoint3=ro_touchpoint3,ro_touchpoint4=ro_touchpoint4).exclude(id=rtratemaster_id).exists():
                if rtratemaster_id == 0:
                    new_rate = form.save()
                    print("Transport Route Rate master Form saved")
                    messages.success(request, 'Record Updated Successfully')
                    url = new_rate.get_absolute_url_trans_route_ratemaster()
                    # return redirect(url)
                    return redirect('/SMS/rtratemaster_list')
                else:
                    rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
                    form = RtratemasteraddForm(request.POST, instance=rtratemaster)
                    form.save()
                    print("Transport Route Rate master Form saved")
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                print("Transport Route Rate master Form not saved - Duplicate found")
                messages.error(request, 'Duplicate Record Found. Please enter a Unique Values.')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("Transport Route Rate Form not saved")
            messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])

# List rtratemaster
@login_required(login_url='login_page')
def rtratemaster_list(request):
    first_name = request.session.get('first_name')
    search_query = request.GET.get('search', '').strip()
    
    # Base Queryset with select_related to avoid N+1 queries
    rtratemaster_qs = RtratemasterInfo.objects.select_related(
        'ro_fromlocation', 'ro_tolocation', 'ro_vehicletype', 
        'ro_customer', 'ro_customerdepartment', 'ro_vehiclecategory', 'ro_updated_by'
    ).all().order_by('-id')
    
    # Filter if search query exists
    if search_query:
        # Split search terms for multi-word search (e.g. "COMPANY NAME")
        search_terms = search_query.split()
        for term in search_terms:
            rtratemaster_qs = rtratemaster_qs.filter(
                Q(ro_fromlocation__place_name__icontains=term) |
                Q(ro_tolocation__place_name__icontains=term) |
                Q(ro_vehicletype__vt_vehicletype__icontains=term) |
                Q(ro_customer__cu_name__icontains=term) |
                Q(ro_customerdepartment__ct_customerdepartment__icontains=term) |
                Q(ro_vehiclecategory__vc_vehiclecategory__icontains=term)
            )
    
    # Pagination
    paginator = Paginator(rtratemaster_qs, 50) # Reduced for performance
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj' : page_obj,
        'first_name': first_name,
        'search_query': search_query,
    }
    return render(request,"asset_mgt_app/rtratemaster_list.html",context)

#Delete rtratemaster
@login_required(login_url='login_page')
def rtratemaster_delete(request,rtratemaster_id):
    rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
    rtratemaster.delete()
    return redirect('/SMS/rtratemaster_list')