from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect

from ..sub_models.customer_mod import CustomerInfo
from ..sub_models.gatein_mod import Gatein_info
from ..sub_models.unit_info_mod import UnitInfo
from ..views import dsr_send_email_view
from ..forms import Gatein_preaddForm
from django.contrib.auth.decorators import login_required
from ..models import Pregateintruckinfo,Gatein_pre_info
from ..models import User_extInfo,Location_info
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest

# Add WH Job
@transaction.atomic
@login_required(login_url='login_page')
def gatein_pre_add(request, gatein_pre_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_branch = User_extInfo.objects.get(user_id=user_id).emp_branch
    user_branch_id=Location_info.objects.get(loc_name=user_branch).id
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = User_extInfo.objects.get(user=user_id).emp_role.id
    print('user_branch_id',user_branch_id)
    print('role',role)
    if request.method == "GET":
        if gatein_pre_id == 0:
            print("I am inside Get add Pre Gatein")
            gatein_pre_form = Gatein_preaddForm()
            context = {
                'first_name': first_name,
                'gatein_pre_form': gatein_pre_form,
                'user_branch_id': user_branch_id,
                'user_id': user_id,
                'role': role,
                'role_id': role_id,
            }
        else:
            gatein_pre_info = Gatein_pre_info.objects.get(pk=gatein_pre_id)
            gatein_pre_email_count = Gatein_pre_info.objects.get(pk=gatein_pre_id).gatein_pre_email_count
            gatein_num_id = Gatein_pre_info.objects.get(pk=gatein_pre_id).id
            request.session['gatein_num_id'] = gatein_num_id
            request.session['ses_pre_gatein_id'] = gatein_pre_id
            user_branch_id = gatein_pre_info.gatein_pre_branch.id if gatein_pre_info.gatein_pre_branch else user_branch_id
            user_branch = gatein_pre_info.gatein_pre_branch.loc_name if gatein_pre_info.gatein_pre_branch else user_branch
            print('gatein_pre_id',gatein_pre_id)
            gatein_pre_form = Gatein_preaddForm(instance=gatein_pre_info)
            pregateintruck_list = Pregateintruckinfo.objects.filter(pregatein_number=gatein_num_id)
            context = {
            'first_name': first_name,
            'gatein_pre_email_count': gatein_pre_email_count,
            'gatein_pre_form': gatein_pre_form,
            'user_branch_id': user_branch_id,
            'user_branch': user_branch,
            'user_id': user_id,
            'pregateintruck_list': pregateintruck_list,
            'role': role,
            'role_id': role_id,
        }
        return render(request, "asset_mgt_app/gatein_pre_add.html", context)
    else:
        if gatein_pre_id == 0:
            print("I am inside post add Pre-Gatein")
            gatein_pre_form = Gatein_preaddForm(request.POST,request.FILES)
            if gatein_pre_form.is_valid():
                print("Pre-Gate-in Main Form is Valid")
                gatein_pre_form.save()

                # Get unit name and branch info from session
                unit_id = request.session.get('ses_unit_id')
                user_branch = request.session.get('ses_unit_name')  # or actual branch name
                # user_branch_id = Location_info.objects.get(loc_name=user_branch).id

                # Map branch ID to code
                branch_code_map = {
                    1: "BLR",
                    2: "MAA",
                    4: "HYD"
                }
                branch_code = branch_code_map.get(user_branch_id, "UNK")  # fallback to UNK

                # Get last inserted ID
                try:
                    last_id = Gatein_pre_info.objects.order_by('-id').values_list('id', flat=True).first()
                    seq_number = 2000000 + last_id
                except ObjectDoesNotExist:
                    last_id = None
                    seq_number = 2000000

                # Construct number
                pre_gatein_num = f"{branch_code}_{user_branch}_{seq_number}"

                # Update record
                if last_id:
                    Gatein_pre_info.objects.filter(id=last_id).update(gatein_pre_number=pre_gatein_num)
                messages.success(request, 'Record Updated Successfully')
                url = 'gatein_pre_update/' + str(last_id)
                return redirect(url)
            else:
                print("Pre-Gate-in Main Form is In-Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("I am inside post edit Pre Gatein")
            gatein_pre_info = Gatein_pre_info.objects.get(pk=gatein_pre_id)
            gatein_pre_form = Gatein_preaddForm(request.POST,request.FILES,instance=gatein_pre_info)
            request.session['ses_pre_gatein_id'] = gatein_pre_id
            if gatein_pre_form.is_valid():
                print("Main Form is Valid")
                gatein_pre_form.save()
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Main Form is In-Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])
            # return redirect('/SMS/gatein_pre_list')
# List WH Job
@login_required(login_url='login_page')
def gatein_pre_list(request):
    first_name = request.session.get('first_name')
    unit_id = request.session.get('ses_unit_id')
    user_id = request.session.get('ses_userID')
    user_branch = User_extInfo.objects.get(user_id=user_id).emp_branch
    user_branch_id = Location_info.objects.get(loc_name=user_branch).id

    unit_name = None
    pending_count = 0

    if unit_id:
        try:
            unit_obj = UnitInfo.objects.get(id=unit_id)
            unit_name = unit_obj.unit_name
            # Pending count (status_id = 6)
            pending_count = Gatein_pre_info.objects.filter(
                gatein_pre_status_id=6,
                gatein_pre_branch_id=unit_id
            ).count()
            # Filter only for this unit
            Gatein_pre_list = Gatein_pre_info.objects.all().order_by('-id')
        except UnitInfo.DoesNotExist:
            unit_name = None
            pending_count = 0
            Gatein_pre_list = Gatein_pre_info.objects.all().order_by('-id')
    else:
        Gatein_pre_list = Gatein_pre_info.objects.all().order_by('-id')

    page_number = request.GET.get('page')
    paginator = Paginator(Gatein_pre_list, 1000)
    page_obj = paginator.get_page(page_number)

    context = {
        'first_name': first_name,
        'page_obj': page_obj,
        'unit_name': unit_name,
        'pending_count': pending_count,
        'total_count': Gatein_pre_list.count(),
    }
    return render(request, "asset_mgt_app/gatein_pre_list.html", context)

#Delete WH Job
@login_required(login_url='login_page')
def gatein_pre_delete(request,gatein_pre_id):
    gatein_pre_del = Gatein_pre_info.objects.get(pk=gatein_pre_id)
    gatein_pre_number_sess = Gatein_pre_info.objects.get(pk=gatein_pre_id).gatein_pre_number
    gatein_truck_del=Pregateintruckinfo.objects.filter(pregatein_number=gatein_pre_id)
    gatein_pre_del.delete()
    gatein_truck_del.delete()
    return redirect('/SMS/pre_gatein_search')
@login_required(login_url='login_page')
def pre_gatein_search(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_unit = (request.session.get('ses_unit_name') or "").strip()

    # Dynamically get branch from User_extInfo and Location_info like in gatein_pre_add
    try:
        user_branch = User_extInfo.objects.get(user_id=user_id).emp_branch
        user_branch_obj = Location_info.objects.get(loc_name=user_branch)
        branch_code_map = {
            1: "BLR",
            2: "MAA",
            4: "HYD"
        }
        branch_code = branch_code_map.get(user_branch_obj.id, "UNK")
    except ObjectDoesNotExist:
        branch_code = "UNK"
        user_branch = ""
        print("DEBUG: Branch info not found for user_id", user_id)

    # Search filters
    pre_gate_in = request.GET.get("pre_gate_in") or ""
    truck_number = request.GET.get("truck_number") or ""
    driver_name = request.GET.get("driver_name") or ""

    Gatein_pre_list = Gatein_pre_info.objects.filter(
        (Q(gatein_pre_number__icontains=pre_gate_in) | Q(gatein_pre_number__isnull=True)) &
        (Q(gatein_pre_truck_number__icontains=truck_number) | Q(gatein_pre_truck_number__isnull=True)) &
        (Q(gatein_pre_driver_name__icontains=driver_name) | Q(gatein_pre_driver_name__isnull=True))
    ).order_by('-id')

    # Pagination
    page_number = request.GET.get('page')
    paginator = Paginator(Gatein_pre_list, 50)
    page_obj = paginator.get_page(page_number)

    # Pending and total counts based on unit pattern
    pending_count = 0
    total_count = 0
    if user_unit:
        unit_pattern = f"{branch_code}_{user_unit}"
        print(f"DEBUG: unit_pattern={unit_pattern}")

        records = Gatein_pre_info.objects.filter(
            gatein_pre_number__icontains=unit_pattern,
            gatein_pre_status=6
        )
        total = Gatein_pre_info.objects.filter(
            gatein_pre_number__icontains=unit_pattern,
        )
        print(f"DEBUG: matching gatein_pre_number = {[r.gatein_pre_number for r in records]}")

        pending_count = records.count()
        total_count = total.count()

    context = {
        'Gatein_pre_list': Gatein_pre_list,
        'first_name': first_name,
        'page_obj': page_obj,
        'user_unit': user_unit,
        'branch_code': branch_code,
        'pending_count': pending_count,
        'total_count': total_count,
    }

    return render(request, "asset_mgt_app/gatein_pre_list.html", context)

@login_required(login_url='login_page')
def gate_in_email(request):
    """
    Handles the Gate In email functionality.
    Retrieves the pre_gatein_id from the session, fetches associated customer names,
    and sends an email if all customers are the same. Otherwise, returns an appropriate response.
    """

    # Retrieve the gatein ID from the session
    pre_gatein_id = request.session.get('ses_pre_gatein_id')
    print("gatein_id",pre_gatein_id)
    if not pre_gatein_id:
        return HttpResponseBadRequest("No Gate In ID found in session.")  # Return a 400 Bad Request response

    # Fetch the list of customer names associated with the gatein_pre_id
    customer_id = list(Gatein_info.objects.filter(gatein_pre_id=pre_gatein_id).values_list('gatein_customer', flat=True))
    customer_names = list(Gatein_info.objects.filter(gatein_pre_id=pre_gatein_id).values_list('gatein_customer', flat=True))
    # Check if all customer names are identical
    if len(customer_id) == 0:
        # return HttpResponseBadRequest("No customers found for the given Gate In ID.")  # No customers found
        messages.success(request, f"No customers found for the given Gate In ID")
        return redirect(request.META['HTTP_REFERER'])
    if len(set(customer_id)) == 1:
        # All values are identical, get the single customer name
        single_customer = customer_id[0]
        customer_name=CustomerInfo.objects.get(pk=single_customer).cu_name
        print(f"Single customer found: {single_customer}")
        subject = f"{customer_name}_Gate-In Alert"
        # Call the email sending function
        gate_in_email_count=Gatein_pre_info.objects.get(pk=pre_gatein_id).gatein_pre_email_count
        print("gate_in_email_count",gate_in_email_count)
        dsr_send_email_view(request, pre_gatein_id, customer_name=single_customer,subject=subject)
        gate_in_email_count = gate_in_email_count + 1
        Gatein_pre_info.objects.filter(pk=pre_gatein_id).update(gatein_pre_email_count=gate_in_email_count)
        # return HttpResponse(f"Email sent to {single_customer}.")
        messages.success(request, f"Gatein details shared to {customer_name} customer.")
        return redirect(request.META['HTTP_REFERER'])
    else:
        # More than one unique customer found
        customer_list = ", ".join(customer_names)
        print(f"More than one customer found: {customer_list}")
        # return HttpResponse(f"More than one customer found: {customer_list}")
        messages.success(request, f"More than one customer found: {customer_list}")
        return redirect(request.META['HTTP_REFERER'])