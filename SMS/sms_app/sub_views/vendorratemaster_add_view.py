from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..forms import VendorratemasteraddForm
from ..models import VendorratemasterInfo1
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator

@login_required(login_url='login_page')
def vendorratemaster_add(request,vendorratemaster_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if vendorratemaster_id == 0:
            form = VendorratemasteraddForm()
        else:
            vendorratemaster = VendorratemasterInfo1.objects.get(pk=vendorratemaster_id)
            form = VendorratemasteraddForm(instance=vendorratemaster)
        return render(request, "asset_mgt_app/vendorratemaster_add.html", {'form': form,'first_name': first_name,'user_id':user_id,})
    else:
        form = VendorratemasteraddForm(request.POST)
        if form.is_valid():
            # Check for duplicates before saving
            vr1_fromlocation = form.cleaned_data['vr1_fromlocation']
            vr1_tolocation = form.cleaned_data['vr1_tolocation']
            vr1_vehicletype = form.cleaned_data['vr1_vehicletype']
            vr1_vendor = form.cleaned_data['vr1_vendor']
            vr1_vehiclecategory = form.cleaned_data['vr1_vehiclecategory']
            vr1_touchpoint = form.cleaned_data['vr1_touchpoint']
            vr1_touchpoint2 = form.cleaned_data['vr1_touchpoint2']
            vr1_touchpoint3 = form.cleaned_data['vr1_touchpoint3']
            vr1_touchpoint4 = form.cleaned_data['vr1_touchpoint4']
            if not VendorratemasterInfo1.objects.filter(vr1_fromlocation=vr1_fromlocation,vr1_tolocation=vr1_tolocation,vr1_vehicletype=vr1_vehicletype,vr1_vendor=vr1_vendor,vr1_vehiclecategory=vr1_vehiclecategory,vr1_touchpoint=vr1_touchpoint,vr1_touchpoint2=vr1_touchpoint2,vr1_touchpoint3=vr1_touchpoint3,vr1_touchpoint4=vr1_touchpoint4).exclude(id=vendorratemaster_id).exists():
                if vendorratemaster_id == 0:
                    new_rate = form.save()
                    print("Vendor Route Rate master Form saved")
                    messages.success(request, 'Record Updated Successfully')
                    #url = new_rate.get_absolute_url_trans_route_ratemaster()
                    # return redirect(url)
                    return redirect('/SMS/vendorratemaster_list')
                else:
                    vendorratemaster = VendorratemasterInfo1.objects.get(pk=vendorratemaster_id)
                    form = VendorratemasteraddForm(request.POST, instance=vendorratemaster)
                    form.save()
                    print("Transport Route Rate master Form saved")
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                print("Vendor Route Rate master Form not saved - Duplicate found")
                messages.error(request, 'Duplicate Record Found. Please enter a Unique Values.')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("Vendor Route Rate Form not saved")
            messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])

# List rtratemaster
@login_required(login_url='login_page')
def vendorratemaster_list(request):
    first_name = request.session.get('first_name')
    search_query = request.GET.get('search', '').strip()
    per_page = request.GET.get('per_page', '50').strip()

    # Base Queryset with select_related to avoid N+1 queries
    vendorratemaster_qs = VendorratemasterInfo1.objects.select_related(
        'vr1_fromlocation', 'vr1_tolocation', 'vr1_vehicletype', 
        'vr1_vendor', 'vr1_vehiclecategory', 'vr1_updated_by'
    ).all().order_by('-id')

    # Filter if search query exists
    if search_query:
        # Split search terms for multi-word search (e.g. "MANJUNATHA TRANSPORT")
        search_terms = search_query.split()
        for term in search_terms:
            vendorratemaster_qs = vendorratemaster_qs.filter(
                Q(vr1_fromlocation__place_name__icontains=term) |
                Q(vr1_tolocation__place_name__icontains=term) |
                Q(vr1_vehicletype__vt_vehicletype__icontains=term) |
                Q(vr1_vendor__vend_name__icontains=term) |
                Q(vr1_vehiclecategory__vc_vehiclecategory__icontains=term)
            )

    # Pagination
    if per_page == 'All':
        count = max(1, vendorratemaster_qs.count())
        paginator = Paginator(vendorratemaster_qs, count)
    else:
        try:
            limit = int(per_page)
        except ValueError:
            limit = 50
        paginator = Paginator(vendorratemaster_qs, limit)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj' : page_obj,
        'first_name': first_name,
        'search_query': search_query,
        'per_page': per_page,
    }
    return render(request,"asset_mgt_app/vendorratemaster_list.html",context)

#Delete vendorratemaster
@login_required(login_url='login_page')
def vendorratemaster_delete(request,vendorratemaster_id):
    vendorratemaster = VendorratemasterInfo1.objects.get(pk=vendorratemaster_id)
    vendorratemaster.delete()
    return redirect('/SMS/vendorratemaster_list')