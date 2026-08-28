from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..forms import RtratemasteraddForm
from ..models import RtratemasterInfo, RtratemasterHistory, MyUser
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator

@login_required(login_url='login_page')
def rtratemaster_add(request, rtratemaster_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_obj = MyUser.objects.filter(pk=user_id).first() if user_id else None

    if request.method == "GET":
        if rtratemaster_id == 0:
            form = RtratemasteraddForm()
        else:
            rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
            form = RtratemasteraddForm(instance=rtratemaster)
        return render(request, "asset_mgt_app/rtratemaster_add.html", {'form': form, 'first_name': first_name, 'user_id': user_id})
    else:
        form = RtratemasteraddForm(request.POST)
        if form.is_valid():
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
            new_rate_val = form.cleaned_data['ro_rate']

            if not RtratemasterInfo.objects.filter(
                ro_fromlocation=ro_fromlocation, ro_tolocation=ro_tolocation,
                ro_vehicletype=ro_vehicletype, ro_customer=ro_customer,
                ro_customerdepartment=ro_customerdepartment, ro_vehiclecategory=ro_vehiclecategory,
                ro_touchpoint=ro_touchpoint, ro_touchpoint2=ro_touchpoint2,
                ro_touchpoint3=ro_touchpoint3, ro_touchpoint4=ro_touchpoint4
            ).exclude(id=rtratemaster_id).exists():
                if rtratemaster_id == 0:
                    new_rate = form.save()
                    # Log Audit History
                    RtratemasterHistory.objects.create(
                        rate_master=new_rate,
                        old_rate=None,
                        new_rate=new_rate_val,
                        action_type='CREATE',
                        changed_by=user_obj or new_rate.ro_updated_by,
                        remarks="Initial creation"
                    )
                    messages.success(request, 'Record Updated Successfully')
                    return redirect('/SMS/rtratemaster_list')
                else:
                    rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
                    old_rate_val = rtratemaster.ro_rate
                    form = RtratemasteraddForm(request.POST, instance=rtratemaster)
                    updated_item = form.save()

                    # Log Audit History if rate changed or updated
                    RtratemasterHistory.objects.create(
                        rate_master=updated_item,
                        old_rate=old_rate_val,
                        new_rate=new_rate_val,
                        action_type='UPDATE',
                        changed_by=user_obj or updated_item.ro_updated_by,
                        remarks=f"Rate updated from ₹{old_rate_val} to ₹{new_rate_val}" if old_rate_val != new_rate_val else "Record updated"
                    )
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                messages.error(request, 'Duplicate Record Found. Please enter a Unique Values.')
                return redirect(request.META['HTTP_REFERER'])
        else:
            messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])

# List rtratemaster
@login_required(login_url='login_page')
def rtratemaster_list(request):
    first_name = request.session.get('first_name')
    search_query = request.GET.get('search', '').strip()
    per_page = request.GET.get('per_page', '50').strip()
    
    rtratemaster_qs = RtratemasterInfo.objects.select_related(
        'ro_fromlocation', 'ro_tolocation', 'ro_vehicletype', 
        'ro_customer', 'ro_customerdepartment', 'ro_vehiclecategory', 'ro_updated_by'
    ).all().order_by('-id')
    
    if search_query:
        clean_query = search_query.replace('₹', '').replace(',', '')
        search_terms = clean_query.split()
        for term in search_terms:
            rtratemaster_qs = rtratemaster_qs.filter(
                Q(ro_fromlocation__place_name__icontains=term) |
                Q(ro_tolocation__place_name__icontains=term) |
                Q(ro_vehicletype__vt_vehicletype__icontains=term) |
                Q(ro_customer__cu_name__icontains=term) |
                Q(ro_customerdepartment__ct_customerdepartment__icontains=term) |
                Q(ro_vehiclecategory__vc_vehiclecategory__icontains=term) |
                Q(ro_rate__icontains=term)
            )
    
    if per_page == 'All':
        count = max(1, rtratemaster_qs.count())
        paginator = Paginator(rtratemaster_qs, count)
    else:
        try:
            limit = int(per_page)
        except ValueError:
            limit = 50
        paginator = Paginator(rtratemaster_qs, limit)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj' : page_obj,
        'first_name': first_name,
        'search_query': search_query,
        'per_page': per_page,
    }
    return render(request, "asset_mgt_app/rtratemaster_list.html", context)

from django.utils import timezone

# Audit History JSON view for modal
@login_required(login_url='login_page')
def rtratemaster_history(request, rtratemaster_id):
    history_logs = RtratemasterHistory.objects.filter(rate_master_id=rtratemaster_id).select_related('changed_by').order_by('-changed_at')
    data = []
    for log in history_logs:
        changed_by_name = log.changed_by.get_full_name() if log.changed_by and log.changed_by.get_full_name() else (log.changed_by.username if log.changed_by else "System/Admin")
        local_changed_at = timezone.localtime(log.changed_at) if log.changed_at else None
        data.append({
            'id': log.id,
            'old_rate': log.old_rate,
            'new_rate': log.new_rate,
            'action_type': log.action_type,
            'changed_by': changed_by_name,
            'changed_at': local_changed_at.strftime('%d-%m-%Y %I:%M %p') if local_changed_at else '',
            'remarks': log.remarks or ''
        })
    return JsonResponse({'history': data})


# Delete rtratemaster
@login_required(login_url='login_page')
def rtratemaster_delete(request, rtratemaster_id):
    rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
    rtratemaster.delete()
    return redirect('/SMS/rtratemaster_list')