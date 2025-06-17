from django.contrib.auth.decorators import login_required
from django.contrib.messages.context_processors import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils import timezone
from ..models import Customerattach,PkcostingInfo,RequirementsInfo,PkstockpurchasesInfo,Loadingbay_Info,TrbusinesstypeInfo,User_extInfo,Warehouse_goods_info,AssetInfo,Vendor_info,Location_info,Product_info,User,Service_Info,TripdetailInfo
from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from datetime import timedelta


@login_required(login_url='login_page')
def home_page(request):
    first_name=request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_ext = User_extInfo.objects.get(user=user_id)
    role=User_extInfo.objects.get(user=user_id).emp_role
    department=User_extInfo.objects.get(user=user_id).department
    bussiness_solution=User_extInfo.objects.get(user=user_id).emp_organisation
    ses_username = request.session.get('ses_username', request.POST.get('username'))
    case_to_case=str(TrbusinesstypeInfo.objects.get(id=1))
    exlcusive=str(TrbusinesstypeInfo.objects.get(id=2))
    dedicated=str(TrbusinesstypeInfo.objects.get(id=3))
    house_hold=str(TrbusinesstypeInfo.objects.get(id=4))
    case_to_case_list=list(Warehouse_goods_info.objects.filter(wh_voucher_num=None,wh_check_in_out=2,wh_customer_type=1).values_list('wh_job_no',flat=True).distinct())
    dedicated_list=list(Warehouse_goods_info.objects.filter(wh_voucher_num=None,wh_check_in_out=2,wh_customer_type=3).values_list('wh_job_no',flat=True).distinct())
    exclusive_list=list(Warehouse_goods_info.objects.filter(wh_voucher_num=None,wh_check_in_out=1,wh_customer_type=2).values_list('wh_job_no',flat=True).distinct())
    wh_check_in_jobs_1 = (Warehouse_goods_info.objects.filter(wh_check_in_out=1).values('wh_job_no')).distinct()
    wh_check_in_jobs_2 = (Loadingbay_Info.objects.filter(lb_validity_date__lte=(timezone.now())+timedelta(days=1),lb_job_no__in=wh_check_in_jobs_1)).distinct()
    wh_job_count=len(wh_check_in_jobs_2)
    open_requirements=len(RequirementsInfo.objects.filter(Q(req_status=2) | Q(req_status=6)))
    count_return=len(PkcostingInfo.objects.filter(ct_excess_status=1))
    excess_count=len(PkcostingInfo.objects.filter(ct_excess_status=3))
    count_retrival=len(PkcostingInfo.objects.filter(ct_cost_type=8,ct_stock_status__in=[1, 3]))
    count_acceptance=len(PkcostingInfo.objects.filter(ct_cost_type=8,ct_stock_status=2))
    customer_contract_due_count = len(Customerattach.objects.filter(ca_contract_due_days__lte=30,ca_status=1))
    customer_rate_due_count = len(Customerattach.objects.filter(ca_rate_due_days__lte=30,ca_status=1))
    total_dues = customer_contract_due_count + customer_rate_due_count
    approval_count = TripdetailInfo.objects.filter( Q(tr_consignmentnumber__isnull=False),
        Q(tr_approval__isnull=True) | Q(tr_approval__ta_approval_status__id=3)
    ).count()

    context = {'count_asset': AssetInfo.objects.all().count(),
               'count_vendors': Vendor_info.objects.filter(vend_status=1).count(),
               'count_ass_asset': AssetInfo.objects.filter(asset_assignedto__isnull=False).count(),
               'count_unass_asset': AssetInfo.objects.filter(asset_assignedto__isnull=True).count(),
               'count_location': Location_info.objects.filter(loc_status=1).count(),
               'count_product': Product_info.objects.all().count(),
               'count_employee': User.objects.all().count(),
               'sum_ass_cost': AssetInfo.objects.aggregate(sum=Sum('asset_cost'))['sum'] or 0.00,
               'sum_service_cost':Service_Info.objects.aggregate(sum=Sum('ser_cost'))['sum'] or 0.00,
               'ses_username': ses_username,
               'first_name': first_name,
               'case_to_case_list': len(case_to_case_list),
               'dedicated_list': len(dedicated_list),
               'exclusive_list': len(exclusive_list),
               'role': role,
               'user_id': user_id,
               'department': department,
               'bussiness_solution': bussiness_solution,
               'bussiness_solution_id': user_ext.emp_organisation.id,
               'wh_job_count': wh_job_count,
               'wh_check_in_jobs_2': wh_check_in_jobs_2,
               'open_requirements': open_requirements,
               'count_return': count_return,
               'excess_count': excess_count,
               'count_retrival': count_retrival,
               'count_acceptance': count_acceptance,
               'customer_contract_due_count': customer_contract_due_count,
               'customer_rate_due_count': customer_rate_due_count,
               'total_dues': total_dues,
               'approval_count':approval_count
               }
    return render(request, 'asset_mgt_app/home_page.html', context)

@login_required(login_url='login_page')
def wh_e_way_bill_list(request):
    wh_check_in_jobs_1 = (Warehouse_goods_info.objects.filter(wh_check_in_out=1).values('wh_job_no')).distinct()
    wh_check_in_jobs_2 = (Loadingbay_Info.objects.filter(lb_validity_date__lte=(timezone.now())+timedelta(days=1),lb_job_no__in=wh_check_in_jobs_1)).distinct()
    first_name = request.session.get('first_name')
    context = {
                'wh_check_in_jobs_2' : wh_check_in_jobs_2,
                'first_name': first_name
            }
    return render(request,"asset_mgt_app/wh_e_way_bill_list.html",context)
@login_required(login_url='login_page')
def edit_wh_e_way_bill_list(request,wh_job_id):
    # wh_job_list_id=Loadingbay_Info.objects.get(pk=wh_job_id)
    # job_id = Gatein_info.objects.get(gatein_job_no=wh_job_num_next).id
    url = 'loadingbay_update/' + str(wh_job_id)
    return redirect(url)

@login_required(login_url='login_page')
def open_requirements_list(request):
    first_name = request.session.get('first_name')
    requirements_list = RequirementsInfo.objects.filter(Q(req_status=2) | Q(req_status=6)).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(requirements_list, 10000)
    page_obj = paginator.get_page(page_number)
    context = {
        'requirements_list': requirements_list,
        'first_name': first_name,
        'page_obj': page_obj,
    }
    return render(request, "asset_mgt_app/requirements_list.html", context)


@login_required(login_url='login_page')
def customer_contract_rate_due_days(request):
    first_name = request.session.get('first_name')
    customer_attach_list = Customerattach.objects.all()

    for i in customer_attach_list:
        customer_attach_id = i.id
        ca_contract_end_date_val = i.ca_contract_end_date
        ca_rate_due_days_val = i.ca_rate_end_date

        if ca_contract_end_date_val:
            try:
                ca_contract_due_days = (ca_contract_end_date_val - timezone.now().date()).days
                Customerattach.objects.filter(pk=customer_attach_id).update(ca_contract_due_days=ca_contract_due_days)
            except Exception as e:
                print("Error calculating ca_contract_due_days:", e)

        if ca_rate_due_days_val:
            try:
                ca_rate_due_days = (ca_rate_due_days_val - timezone.now().date()).days
                Customerattach.objects.filter(pk=customer_attach_id).update(ca_rate_due_days=ca_rate_due_days)
            except Exception as e:
                print("Error calculating ca_rate_due_days:", e)

    # Return an empty HTTP response
    return HttpResponse(status=204)

@login_required(login_url='login_page')
def customer_contract_rate_dues_list(request):
    first_name = request.session.get('first_name')
    customer_attach_list = Customerattach.objects.filter(Q(ca_contract_due_days__lte=30) | Q(ca_rate_due_days__lte=30))
    context = {
        'customer_attach_list': customer_attach_list,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/customer_contract_rate_due_days_list.html", context)
