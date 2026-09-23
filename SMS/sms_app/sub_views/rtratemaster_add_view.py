import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..forms import RtratemasteraddForm
from ..models import RtratemasterInfo, RtratemasterHistory, MyUser
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator

from .general_utils import is_admin_user


@login_required(login_url='login_page')
def rtratemaster_add(request, rtratemaster_id=0):
    if not is_admin_user(request):
        messages.error(request, "Access Restricted: You do not have permission to add or modify Route Rate Master records.")
        return redirect('home_page')

    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_obj = MyUser.objects.filter(pk=user_id).first() if user_id else None

    if request.method == "GET":
        if rtratemaster_id == 0:
            form = RtratemasteraddForm()
        else:
            rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
            if rtratemaster.ro_validity_to and rtratemaster.ro_validity_to < datetime.date.today() and rtratemaster.ro_status == 'Active':
                rtratemaster.ro_status = 'Inactive'
                rtratemaster.save(update_fields=['ro_status'])
            form = RtratemasteraddForm(instance=rtratemaster)

        # Pop affected enquiries from session (set after a rate/validity change)
        affected_data = request.session.pop('rate_affected_enquiries', None)
        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'affected_enquiries': affected_data.get('enquiries') if affected_data else None,
            'new_rate': affected_data.get('new_rate') if affected_data else None,
            'old_rate': affected_data.get('old_rate') if affected_data else None,
            'validity_from': affected_data.get('validity_from') if affected_data else None,
            'validity_to': affected_data.get('validity_to') if affected_data else None,
            'has_differing_rates': affected_data.get('has_differing_rates') if affected_data else False,
        }
        return render(request, "asset_mgt_app/rtratemaster_add.html", context)

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
            # Capture validity dates from form BEFORE form variable is overwritten
            new_val_from = form.cleaned_data.get('ro_validity_from')
            new_val_to = form.cleaned_data.get('ro_validity_to')

            if not RtratemasterInfo.objects.filter(
                ro_fromlocation=ro_fromlocation, ro_tolocation=ro_tolocation,
                ro_vehicletype=ro_vehicletype, ro_customer=ro_customer,
                ro_customerdepartment=ro_customerdepartment, ro_vehiclecategory=ro_vehiclecategory,
                ro_touchpoint=ro_touchpoint, ro_touchpoint2=ro_touchpoint2,
                ro_touchpoint3=ro_touchpoint3, ro_touchpoint4=ro_touchpoint4
            ).exclude(id=rtratemaster_id).exists():
                curr_user = user_obj if user_obj else (request.user if request.user.is_authenticated else None)

                if rtratemaster_id == 0:
                    # CREATE
                    new_rate = form.save(commit=False)
                    if curr_user:
                        new_rate.ro_updated_by = curr_user
                    new_rate.save()
                    RtratemasterHistory.objects.create(
                        rate_master=new_rate,
                        old_rate=None,
                        new_rate=new_rate_val,
                        old_agreement_type=None,
                        new_agreement_type=new_rate.ro_agreement_type,
                        old_validity_from=None,
                        new_validity_from=new_rate.ro_validity_from,
                        old_validity_to=None,
                        new_validity_to=new_rate.ro_validity_to,
                        action_type='CREATE',
                        changed_by=curr_user or new_rate.ro_updated_by,
                        remarks="Initial creation"
                    )
                    messages.success(request, 'Record Updated Successfully')
                    return redirect('/SMS/rtratemaster_list')

                else:
                    # UPDATE - capture old values from DB before saving
                    rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
                    old_rate_val = rtratemaster.ro_rate
                    old_ag_type = rtratemaster.ro_agreement_type
                    old_val_from = rtratemaster.ro_validity_from
                    old_val_to = rtratemaster.ro_validity_to

                    form2 = RtratemasteraddForm(request.POST, instance=rtratemaster)
                    updated_item = form2.save(commit=False)
                    if curr_user:
                        updated_item.ro_updated_by = curr_user
                    updated_item.save()

                    RtratemasterHistory.objects.create(
                        rate_master=updated_item,
                        old_rate=old_rate_val,
                        new_rate=new_rate_val,
                        old_agreement_type=old_ag_type,
                        new_agreement_type=updated_item.ro_agreement_type,
                        old_validity_from=old_val_from,
                        new_validity_from=updated_item.ro_validity_from,
                        old_validity_to=old_val_to,
                        new_validity_to=updated_item.ro_validity_to,
                        action_type='UPDATE',
                        changed_by=curr_user or updated_item.ro_updated_by,
                        remarks="Rate updated from Rs{} to Rs{}".format(old_rate_val, new_rate_val) if old_rate_val != new_rate_val else "Record updated"
                    )

                    # ── Trigger conditions ──
                    rate_changed = (float(new_rate_val) != float(old_rate_val))
                    validity_from_changed = (old_val_from != new_val_from)
                    validity_to_changed = (old_val_to != new_val_to)

                    print("[DEBUG RATE GAP] rate_changed={}, validity_from_changed={}, validity_to_changed={}".format(
                        rate_changed, validity_from_changed, validity_to_changed))
                    print("[DEBUG RATE GAP] old_rate={}, new_rate={}, old_from={}, new_from={}, old_to={}, new_to={}".format(
                        old_rate_val, new_rate_val, old_val_from, new_val_from, old_val_to, new_val_to))
                        
                    with open('popup_debug.txt', 'a') as debug_f:
                        debug_f.write(f"--- UPDATE ---\n")
                        debug_f.write(f"rate_changed={rate_changed} ({old_rate_val} -> {new_rate_val})\n")
                        debug_f.write(f"from_changed={validity_from_changed} ({old_val_from} -> {new_val_from})\n")
                        debug_f.write(f"to_changed={validity_to_changed} ({old_val_to} -> {new_val_to})\n")

                    if rate_changed or validity_from_changed or validity_to_changed:
                        # Find the union of the old and new validity periods
                        search_from = min(d for d in [old_val_from, new_val_from] if d) if (old_val_from or new_val_from) else None
                        search_to = max(d for d in [old_val_to, new_val_to] if d) if (old_val_to or new_val_to) else None

                        _store_affected_enquiries_in_session(
                            request=request,
                            rate_record=updated_item,
                            search_from=search_from,
                            search_to=search_to,
                            old_rate_val=old_rate_val,
                            new_rate_val=new_rate_val,
                        )
                    else:
                        print("[DEBUG RATE GAP] No trigger condition met - no popup")

                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])

            else:
                messages.error(request, 'Duplicate Record Found. Please enter a Unique Values.')
                return redirect(request.META['HTTP_REFERER'])
        else:
            messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])


def _store_affected_enquiries_in_session(request, rate_record, search_from, search_to, old_rate_val, new_rate_val):
    """
    Finds Enquirynotevehicle records for the same lane+customer that still have
    the OLD rate (env_sale = old_rate_val) within the OLD validity date range,
    and stores them in the session so the popup is shown on next GET.
    """
    from ..sub_models.enquirynote_vehicle_mod import Enquirynotevehicle

    print("[DEBUG RATE GAP] Querying: customer_id={}, from_id={}, to_id={}, old_rate={}, search_from={}, search_to={}".format(
        rate_record.ro_customer_id, rate_record.ro_fromlocation_id,
        rate_record.ro_tolocation_id, old_rate_val, search_from, search_to))

    # Base query: same lane + customer, exclude enquiries that already have the new rate
    affected_envs = Enquirynotevehicle.objects.select_related(
        'env_enquirynumber',
        'env_enquirynumber__en_customername',
        'env_enquirynumber__en_fromlocaion',
        'env_enquirynumber__en_tolocation',
        'env_vehicletype',
        'env_vehiclecategory',
    ).filter(
        env_enquirynumber__en_customername=rate_record.ro_customer,
        env_enquirynumber__en_fromlocaion=rate_record.ro_fromlocation,
        env_enquirynumber__en_tolocation=rate_record.ro_tolocation,
        env_enquirynumber__en_touchpoint=rate_record.ro_touchpoint,
        env_enquirynumber__en_touchpoint2=rate_record.ro_touchpoint2,
        env_enquirynumber__en_touchpoint3=rate_record.ro_touchpoint3,
        env_enquirynumber__en_touchpoint4=rate_record.ro_touchpoint4,
        env_vehicletype=rate_record.ro_vehicletype,
        env_vehiclecategory=rate_record.ro_vehiclecategory,
    ).exclude(
        env_sale=float(new_rate_val)  # skip enquiries already having the new rate
    )

    # Filter by union validity date range
    if search_from:
        affected_envs = affected_envs.filter(env_enquirynumber__en_pickupdatetime__date__gte=search_from)
    if search_to:
        affected_envs = affected_envs.filter(env_enquirynumber__en_pickupdatetime__date__lte=search_to)

    count = affected_envs.count()
    print("[DEBUG RATE GAP] Affected env records found: {}".format(count))
    
    with open('popup_debug.txt', 'a') as debug_f:
        debug_f.write(f"Query count: {count} (search_from={search_from}, search_to={search_to})\n")
        
    if count == 0:
        print("[DEBUG RATE GAP] No records -> no popup")
        return

    enquiries_data = []
    for env in affected_envs:
        enq = env.env_enquirynumber
        env_sale = env.env_sale
        env_special_sale = env.env_special_sale
        same_rates = (
            env_sale is not None and env_special_sale is not None
            and abs(float(env_sale) - float(env_special_sale)) < 0.01
        )
        enquiries_data.append({
            'env_id': env.pk,
            'enquiry_no': enq.en_enquirynumber or str(enq.pk),
            'customer': enq.en_customername.cu_name if enq.en_customername else '',
            'from_location': enq.en_fromlocaion.place_name if enq.en_fromlocaion else '',
            'to_location': enq.en_tolocation.place_name if enq.en_tolocation else '',
            'pickup_date': enq.en_pickupdatetime.strftime('%d-%m-%Y %H:%M') if enq.en_pickupdatetime else '',
            'vehicle_type': env.env_vehicletype.vt_vehicletype if env.env_vehicletype else '',
            'env_sale': env_sale,
            'env_special_sale': env_special_sale,
            'same_rates': same_rates,
        })

    # Sort so that differing rates (same_rates == False) appear at the top
    enquiries_data.sort(key=lambda x: x['same_rates'])
    has_differing_rates = any(not e['same_rates'] for e in enquiries_data)

    request.session['rate_affected_enquiries'] = {
        'enquiries': enquiries_data,
        'new_rate': new_rate_val,
        'old_rate': old_rate_val,
        'validity_from': search_from.strftime('%d-%m-%Y') if search_from else '',
        'validity_to': search_to.strftime('%d-%m-%Y') if search_to else '',
        'has_differing_rates': has_differing_rates,
    }
    print("[DEBUG RATE GAP] Session set with {} enquiries, new_rate={}".format(len(enquiries_data), new_rate_val))


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
        clean_query = search_query.replace('\u20b9', '').replace(',', '')
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
        'page_obj': page_obj,
        'first_name': first_name,
        'search_query': search_query,
        'per_page': per_page,
    }
    return render(request, "asset_mgt_app/rtratemaster_list.html", context)


from django.utils import timezone


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


@login_required(login_url='login_page')
def rtratemaster_delete(request, rtratemaster_id):
    if not is_admin_user(request):
        messages.error(request, "Access Restricted: You do not have permission to delete Route Rate Master records.")
        return redirect('home_page')
    rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
    rtratemaster.delete()
    return redirect('/SMS/rtratemaster_list')


@login_required(login_url='login_page')
def rtratemaster_update_enquiry_rates(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    import json
    try:
        body = json.loads(request.body)
        new_rate = float(body.get('new_rate', 0))
        update_sell_ids = [int(x) for x in body.get('update_sell', [])]
        update_special_ids = [int(x) for x in body.get('update_special', [])]
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        return JsonResponse({'error': 'Invalid data: {}'.format(e)}, status=400)

    from ..sub_models.enquirynote_vehicle_mod import Enquirynotevehicle
    updated_sell = 0
    updated_special = 0
    if update_sell_ids:
        updated_sell = Enquirynotevehicle.objects.filter(pk__in=update_sell_ids).update(env_sale=new_rate)
    if update_special_ids:
        updated_special = Enquirynotevehicle.objects.filter(pk__in=update_special_ids).update(env_special_sale=new_rate)
    return JsonResponse({
        'success': True,
        'updated_sell': updated_sell,
        'updated_special': updated_special,
        'message': 'Updated Sell Rate for {} record(s) and Special Sell Rate for {} record(s).'.format(updated_sell, updated_special)
    })
