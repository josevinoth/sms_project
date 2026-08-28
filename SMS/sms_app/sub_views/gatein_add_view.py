from io import BytesIO
from io import BytesIO
from random import randint
from django.contrib import messages
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa

from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id, get_base64_image
from ..forms import GateinaddForm
from django.contrib.auth.decorators import login_required
from ..models import VehicletypeInfo,Pregateintruckinfo,Location_info,Gatein_info,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info,DamagereportImages,Gatein_pre_info
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from ..models import User_extInfo
import pytz

from ..sub_models.DG_cargo_checklist_mod import DGcargovalueInfo


# Add WH Job
@transaction.atomic
@login_required(login_url='login_page')
def gatein_add(request, gatein_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_branch = User_extInfo.objects.get(user_id=user_id).emp_branch
    user_branch_id = Location_info.objects.get(loc_name=user_branch).id
    ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
    wh_job_id = ses_gatein_id_nam
    tot_package = request.POST.get('gatein_no_of_pkg')
    dg_cargo_list =DGcargovalueInfo.objects.filter(DG_wh_job_no=wh_job_id)

    if request.method == "GET":
        if gatein_id == 0:
            print("I am inside Get add Gatein")
            gatein_form = GateinaddForm()
            context = {
                'user_id': user_id,
                'first_name': first_name,
                'gatein_form': gatein_form,
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'wh_job_id': wh_job_id,
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'user_branch':user_branch,
                'dg_cargo_list':dg_cargo_list,
            }
        else:
            print("I am inside get edit Gatein")
            wh_job_id = Gatein_info.objects.get(pk=gatein_id).gatein_job_no
            wh_customer_name = Gatein_info.objects.get(pk=gatein_id).gatein_customer
            wh_customer_name_id = Gatein_info.objects.get(pk=gatein_id).gatein_customer.id
            wh_customer_type = Gatein_info.objects.get(pk=gatein_id).gatein_customer_type
            wh_customer_type_id = Gatein_info.objects.get(pk=gatein_id).gatein_customer_type.id
            wh_invoice = Gatein_info.objects.get(pk=gatein_id).gatein_invoice
            wh_total_packages = Gatein_info.objects.get(pk=gatein_id).gatein_no_of_pkg
            wh_invoice_weight = Gatein_info.objects.get(pk=gatein_id).gatein_weight
            wh_po_num = Gatein_info.objects.get(pk=gatein_id).gatein_po_num
            request.session['ses_gatein_id_nam'] = wh_job_id
            request.session['ses_customer_name'] = str(wh_customer_name)
            request.session['ses_customer_type'] = str(wh_customer_type)
            request.session['ses_customer_name_id'] = wh_customer_name_id
            request.session['ses_customer_type_id'] = wh_customer_type_id
            request.session['ses_wh_invoice'] = wh_invoice
            request.session['ses_gatein_no_of_pkg'] = wh_total_packages
            request.session['ses_gatein_weight'] = wh_invoice_weight
            request.session['ses_consigner']=Gatein_info.objects.get(pk=gatein_id).gatein_shipper
            request.session['ses_consignee'] = Gatein_info.objects.get(pk=gatein_id).gatein_consignee
            request.session['ses_po_num'] = wh_po_num
            request.session['ses_wh_gatein_id'] = gatein_id
            try:
                damage_status = Warehouse_goods_info.objects.filter(wh_gate_injob_no_id=gatein_id).exclude(wh_damage_check_id=6).values_list('wh_damage_check_id', flat=True).first()
                # If no non-6 values are found, default to 6
                damage_status = damage_status if damage_status is not None else 6
            except ObjectDoesNotExist:
                damage_status = 6
            # Gate In Status Check
            try:
                gatein_status = Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_status  # fetch gatein status
            except ObjectDoesNotExist:
                gatein_status = "No Status"
            # Loading Bay Status Check
            try:
                loadingbay_record = Loadingbay_Info.objects.filter(lb_job_no=wh_job_id).first()
                if loadingbay_record:
                    loadingbay_status = loadingbay_record.lb_status
                else:
                    loadingbay_status = None  # or handle missing case
            except ObjectDoesNotExist:
                loadingbay_status = "No Status"
            # Damage/Before Status Check
            try:
                damage_before_status = DamagereportInfo.objects.get(dam_wh_job_num=wh_job_id).dam_status  # fetch damage report status
            except ObjectDoesNotExist:
                damage_before_status = "No Status"
            # Damage/After Status Check
            try:
                goods_status = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_goods_status',flat=True)  # count records
                goods_status_list = list(goods_status)
                if goods_status_list == []:
                    damage_after_status = "Empty"
                elif all(element == None for element in (goods_status_list)):
                    damage_after_status = "None"
                elif all(element == 5 for element in (goods_status_list)):
                    damage_after_status = "Completed"  # get goods status
                else:
                    damage_after_status = "No Status"  # get goods status
            except ObjectDoesNotExist:
                damage_after_status = "No Status"

            # Warehousein Status Check
            try:
                warehousein_stack_layer = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list(
                    'wh_stack_layer', flat=True)  # count records

                warehousein_stack_layer_list = list(warehousein_stack_layer)
                if warehousein_stack_layer_list == []:
                    warehousein_status = "Empty"
                elif all(element == None for element in (warehousein_stack_layer_list)):
                    warehousein_status = "None"
                elif None not in warehousein_stack_layer_list:
                    warehousein_status = "Completed"  # get goods status
                else:
                    warehousein_status = "No Status"  # get goods status
            except ObjectDoesNotExist:
                warehousein_status = "No Status"
            approved_cargo = DGcargovalueInfo.objects.filter(
                DG_wh_job_no=wh_job_id, DG_wh_approval_status=1
            ).exists()
            print("Approved Cargo:", approved_cargo)
            if approved_cargo:
                Gatein_info.objects.filter(gatein_job_no=wh_job_id).update(gatein_status_id=5)

            loadingbay_list= Loadingbay_Info.objects.filter(lb_job_no=wh_job_id)
            damagereport_list= DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id)
            gatein_list=Gatein_info.objects.filter(gatein_job_no=wh_job_id)
            goods_list= Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id)
            gatein_info = Gatein_info.objects.get(pk=gatein_id)
            gatein_form = GateinaddForm(instance=gatein_info)
            context = {
                'user_id': user_id,
                'gatein_form': gatein_form,
                'first_name': first_name,
                'damagereport_list':damagereport_list,
                'loadingbay_list': loadingbay_list,
                'gatein_list':gatein_list,
                'goods_list': goods_list,
                'gatein_status':gatein_status,
                'loadingbay_status':loadingbay_status,
                'damage_before_status':damage_before_status,
                'damage_after_status': damage_after_status,
                'warehousein_status': warehousein_status,
                'damage_status': damage_status,
                'dg_cargo_list': dg_cargo_list,
            }
        return render(request, "asset_mgt_app/gatein_add.html", context)
    else:
        if gatein_id == 0:
            print("I am inside post add Gatein")
            gatein_form = GateinaddForm(request.POST)
            if gatein_form.is_valid():
                print("Form is Valid")
                instance = gatein_form.save()
                # Determine branch code using centralized utility
                fy = get_financial_year()
                branch_id = get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                prefix = f"{fy}_{branch_code}_WH_"
                wh_job_num_next = generate_next_number(Gatein_info, 'gatein_job_no', prefix, 6)

                Gatein_info.objects.filter(id=instance.id).update(gatein_job_no=wh_job_num_next)
                messages.success(request, 'Record Updated Successfully')
                # job_id = Gatein_info.objects.get(gatein_job_no=wh_job_num_next).id
                url = 'gatein_update/' + str(instance.id)
                return redirect(url)
            else:
                print("Form is In-Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("I am inside post edit Gatein")
            gatein_info = Gatein_info.objects.get(pk=gatein_id)
            gatein_form = GateinaddForm(request.POST, instance=gatein_info)
            if gatein_form.is_valid():
                print("Form is Valid")
                instance = gatein_form.save(commit=False)
                if not instance.gatein_job_no or str(instance.gatein_job_no).lower() == 'none':
                    fy = get_financial_year()
                    branch_id = get_session_branch_id(request)
                    branch_code = get_branch_code(branch_id)
                    prefix = f"{fy}_{branch_code}_WH_"
                    wh_job_num_next = generate_next_number(Gatein_info, 'gatein_job_no', prefix, 6)
                    instance.gatein_job_no = wh_job_num_next
                instance.save()
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Form is In-Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/gatein_list')
# List WH Job

@login_required(login_url='login_page')
def gatein_list(request):
    first_name = request.session.get('first_name')
    Gatein_list= (Gatein_info.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(Gatein_list, 50)  # Standardized to 50
    page_obj = paginator.get_page(page_number)
    context = {
        # 'Gatein_list' : Gatein_list,
        'first_name': first_name,
        'page_obj': page_obj,
    }
    return render(request,"asset_mgt_app/gatein_list.html",context)
@login_required(login_url='login_page')
def get_queryset(request):
    first_name = request.session.get('first_name')
    pre_gate_in = request.GET.get("pre_gate_in")
    job_number = request.GET.get("job_number")
    invoice_number = request.GET.get("invoice_number")
    if not pre_gate_in:
        pre_gate_in = ""
    if not job_number:
        job_number = ""
    if not invoice_number:
        invoice_number = ""
    Gatein_list = (Gatein_info.objects.filter((Q(gatein_job_no__icontains =job_number)|Q(gatein_job_no__isnull=True)) & (Q(gatein_invoice__icontains =invoice_number)|Q(gatein_invoice__isnull=True)) & (Q(gatein_pre_id__gatein_pre_number__icontains =pre_gate_in)|Q(gatein_pre_id__isnull=True)))).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(Gatein_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
        'Gatein_list': Gatein_list,
        'first_name': first_name,
        'page_obj': page_obj,
        'pre_gate_in': pre_gate_in,
        'job_number': job_number,
        'invoice_number': invoice_number,
        }
    return render(request, "asset_mgt_app/gatein_list.html", context)

#Delete WH Job
@login_required(login_url='login_page')
def gatein_delete(request,gatein_id):
    wh_job_id=Gatein_info.objects.get(pk=gatein_id).gatein_job_no
    # wh_job_id = request.session.get('ses_gatein_id_nam')
    gatein_del = Gatein_info.objects.get(pk=gatein_id)
    gatein_del.delete()

    # Delete loading Bay
    try:
        loadingbay_del = Loadingbay_Info.objects.filter(lb_job_no=wh_job_id)
        loadingbay_del.delete()
    except ObjectDoesNotExist:
        print("Loading bay Object does not exist")
        pass

    # Delete Damage/Check Before
    try:
        damagereport_del=DamagereportInfo.objects.get(dam_wh_job_num=wh_job_id)
        damagereportimg_del = DamagereportImages.objects.get(damimage_wh_job_num=wh_job_id)
        damagereport_del.delete()
        damagereportimg_del.delete()
    except ObjectDoesNotExist:
        print("Damage/Check Before Object does not exist")
        pass

    # Delete Damage/Check After
    try:
        Warehouse_goods_del = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id)
        Warehouse_goods_del.delete()
    except ObjectDoesNotExist:
        print("Damage/Check After Object does not exist")
        pass

    return redirect('/SMS/search')

@login_required(login_url='login_page')
def load_pre_gate_in(request):
    pre_gatein_val = request.GET.get('pre_gatein_val')
    pre_gatein_id = Gatein_pre_info.objects.get(gatein_pre_number=pre_gatein_val).id
    pre_gatein_truck_list=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id)
    print('pre_gatein_truck_list',pre_gatein_truck_list)
    truck_numbers=[]
    truck_numbers_id=[]
    for i in pre_gatein_truck_list:
        truck_numbers.append(i.pregatein_truck_number)
        truck_numbers_id.append(i.id)
    data = {
            'truck_numbers_id': truck_numbers_id,
            'truck_numbers': truck_numbers,
        }
    # return HttpResponse(json.dumps(data))
    return JsonResponse(data)

# Load pre-gatein truck details
@login_required(login_url='login_page')
def load_pre_gate_in_truck_details(request):
    # Fetch pre_gate_in details
    pre_gatein_id = request.GET.get('pre_gatein_id')
    pre_gatein_truck_number_val = request.GET.get('gatein_truck_number_val')
    Transporter=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id,pregatein_truck_number=pre_gatein_truck_number_val).values_list('pregatein_transporter_name__transporter_name',flat=True)
    Driver_Name=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id,pregatein_truck_number=pre_gatein_truck_number_val).values_list('pregatein_driver',flat=True)
    Driver_Contact=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id,pregatein_truck_number=pre_gatein_truck_number_val).values_list('pregatein_contact_number',flat=True)
    Driver_License=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id,pregatein_truck_number=pre_gatein_truck_number_val).values_list('pregatein_dl_number',flat=True)
    OTL=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id,pregatein_truck_number=pre_gatein_truck_number_val).values_list('pregatein_otl',flat=True)
    Truck_Number=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id,pregatein_truck_number=pre_gatein_truck_number_val).values_list('pregatein_truck_number',flat=True)
    Truck_Type=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id,pregatein_truck_number=pre_gatein_truck_number_val).values_list('pregatein_truck_type',flat=True)
    dock_in_time = Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id,pregatein_truck_number=pre_gatein_truck_number_val).values_list('pregatein_dock_in_date_time', flat=True)

    # Convert datetime objects to IST timezone
    ist = pytz.timezone('Asia/Kolkata')
    dock_in_time_ist = []
    for dt in dock_in_time:
        if dt is not None:
            dock_in_time_ist.append(dt.astimezone(ist))
        else:
            dock_in_time_ist.append(None)

    # Convert datetime objects to date-time strings in IST
    formatted_dock_in_time = [dt.strftime("%Y-%m-%d %H:%M:%S") if dt is not None else None for dt in dock_in_time_ist]

    Truck_Name=[]
    for i in Truck_Type:
        Truck_Name.append(VehicletypeInfo.objects.get(id=i).vt_vehicletype)
    data = {
            'Transporter': list(Transporter),
            'Driver_Name': list(Driver_Name),
            'Driver_Contact': list(Driver_Contact),
            'Driver_License': list(Driver_License),
            'OTL': list(OTL),
            'Truck_Number':list(Truck_Number),
            'Truck_Type': list(Truck_Name),
            'dock_in_time': formatted_dock_in_time,
        }
    # return HttpResponse(json.dumps(data))
    return JsonResponse((data))

@login_required(login_url='login_page')
def gatein_pdf(request, gatein_id=0, download=False):
    gatein = get_object_or_404(Gatein_info, id=gatein_id)

    # Convert signatures to base64
    gatein.driver_signature_base64 = None
    if hasattr(gatein, "gatein_driver_signature") and gatein.gatein_driver_signature:
        gatein.driver_signature_base64 = get_base64_image(gatein.gatein_driver_signature)

    gatein.supervisor_signature_base64 = None
    if hasattr(gatein, "gatein_supervisor_signature") and gatein.gatein_supervisor_signature:
        gatein.supervisor_signature_base64 = get_base64_image(gatein.gatein_supervisor_signature)

    # Fetch warehouse goods info (matching by job number)
    warehouse_info = Warehouse_goods_info.objects.filter(
        wh_job_no=gatein.gatein_job_no
    ).select_related('wh_damages', 'wh_check_in_out').first()

    context = {
        "gatein": gatein,
        "warehouse": warehouse_info
    }
    template_path = 'asset_mgt_app/gatein_gatepass.html'
    template = get_template(template_path)
    html = template.render(context)

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

    if pisa_status.err:
        raise ValueError("Error generating PDF")

    pdf_buffer.seek(0)
    pdf_data = pdf_buffer.read()
    pdf_buffer.close()

    if download:
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Gatein_{gatein.gatein_job_no or gatein.id}.pdf"'
        return response

    return pdf_data

def get_shippers(request):
    q = request.GET.get('term', '')
    shippers = list(
        Gatein_info.objects.filter(gatein_shipper__icontains=q)
        .values_list('gatein_shipper', flat=True)
        .distinct()[:10]   # limit results
    )
    return JsonResponse(shippers, safe=False)

def get_consignees(request):
        q = request.GET.get('term', '')
        consignees = list(
            Gatein_info.objects.filter(gatein_consignee__icontains=q)
            .values_list('gatein_consignee', flat=True)
            .distinct()[:10]
        )
        return JsonResponse(consignees, safe=False)



@login_required(login_url='login_page')
def gatein_pdf_download(request, gatein_id):
    return gatein_pdf(request, gatein_id, download=True)

@csrf_exempt
@login_required(login_url='login_page')
def gatein_upload_attachment(request, pk, att_type):
    if request.method == 'POST' and request.FILES.get('attachment'):
        instance = get_object_or_404(Gatein_info, pk=pk)
        uploaded_file = request.FILES['attachment']

        if att_type == 'invoice':
            instance.gatein_invoice_att = uploaded_file

        instance.save()
        messages.success(request, 'Attachment uploaded successfully.')
    else:
        messages.error(request, 'Attachment upload failed. Please try again.')

    return redirect(request.META.get('HTTP_REFERER', 'gatein_list'))
@csrf_exempt
@login_required(login_url='login_page')
def gatein_delete_attachment(request, pk, att_type):
    if request.method == 'POST':
        instance = get_object_or_404(Gatein_info, pk=pk)

        if att_type == 'invoice' and instance.gatein_invoice_att:
            instance.gatein_invoice_att.delete(save=False)
            instance.gatein_invoice_att = None

        instance.save()
        messages.success(request, 'Attachment deleted successfully.')

    return redirect(request.META.get('HTTP_REFERER', 'gatein_list'))



from django.http import JsonResponse
from django.urls import reverse

@login_required(login_url='login_page')
def gatein_list_ajax(request):
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')
    
    # Custom form filters from /SMS/search/
    pre_gate_in = request.GET.get('pre_gate_in', '')
    job_number = request.GET.get('job_number', '')
    invoice_number = request.GET.get('invoice_number', '')

    queryset = Gatein_info.objects.select_related('gatein_pre_id', 'gatein_customer', 'gatein_updated_by', 'gatein_status').all()

    # Apply form filters
    if pre_gate_in:
        queryset = queryset.filter(gatein_pre_id__gatein_pre_number__icontains=pre_gate_in)
    if job_number:
        queryset = queryset.filter(gatein_job_no__icontains=job_number)
    if invoice_number:
        queryset = queryset.filter(gatein_invoice__icontains=invoice_number)

    if search_value:
        queryset = queryset.filter(
            Q(id__icontains=search_value) |
            Q(gatein_pre_id__gatein_pre_number__icontains=search_value) |
            Q(gatein_job_no__icontains=search_value) |
            Q(gatein_invoice__icontains=search_value) |
            Q(gatein_customer__cu_name__icontains=search_value)
        )

    total_records = Gatein_info.objects.count()
    filtered_records = queryset.count()
    
    # Ordering
    order_column_index = request.GET.get('order[0][column]', 0)
    order_dir = request.GET.get('order[0][dir]', 'desc')
    
    # These match the columns configured in DataTables JS (from 0 to 11)
    columns = [
        'id', 'id', 'gatein_created_at', 'gatein_pre_id__gatein_pre_number', 
        'id', 'id', 'gatein_job_no', 'gatein_invoice', 
        'gatein_customer__cu_name', 'gatein_updated_at', 'gatein_updated_by__username', 'id'
    ]
    if int(order_column_index) < len(columns):
        order_by = columns[int(order_column_index)]
        if order_dir == 'desc':
            order_by = f"-{order_by}"
        queryset = queryset.order_by(order_by)

    data = []
    for item in queryset[start:start+length]:
        update_url = reverse('gatein_update', args=[item.id])
        delete_url = reverse('gatein_delete', args=[item.id])
        csrf_token = request.COOKIES.get('csrftoken', '')
        
        edit_btn = f'<a href="{update_url}" style="background: #f5a623; color: white; border: none; border-radius: 20px; width: 44px; min-width: 44px; height: 34px; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 2px 5px rgba(245, 166, 35, 0.2); text-decoration: none;" title="Edit"><i class="far fa-edit"></i></a>'
        
        delete_btn = f'''<form action="{delete_url}" method="post" onclick="return confirm('Are you sure?');" style="margin:0; display:inline;">
            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
            <button type="submit" class="btn btn-outline-danger" style="border-radius: 20px; padding: 4px 15px;">
                <i class="fas fa-trash-alt"></i>
            </button>
        </form>'''
        
        # Attachments
        inward_pod = ''
        if item.gatein_invoice_att:
            url = item.gatein_invoice_att.url
            upload_url = reverse('gatein_upload_attachment', args=[item.id, 'invoice'])
            inward_pod = f'''<div style="width: 100px; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: flex; flex-direction: column; background: transparent;">
                <a href="{url}" target="_blank" style="background: #38bdf8; color: #ffffff; border: none; padding: 7px 0; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; text-decoration: none; text-align: center; display: block; width: 100%; line-height: 1.2;">VIEW</a>
                <form method="post" action="{upload_url}" enctype="multipart/form-data" style="margin: 0; padding: 0; width: 100%;">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                    <label style="background: #fbbf24; color: #ffffff; border: none; border-top: 1px solid rgba(255,255,255,0.3); padding: 7px 0; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; text-align: center; cursor: pointer; display: block; width: 100%; margin: 0; line-height: 1.2;">RE-ATTACH<input type="file" name="gatein_invoice_att" style="display: none;" onchange="this.form.submit()"></label>
                </form>
            </div>'''
        else:
            upload_url = reverse('gatein_upload_attachment', args=[item.id, 'invoice'])
            inward_pod = f'''<form method="post" action="{upload_url}" enctype="multipart/form-data" style="margin: 0; padding: 0; width: 100px;">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                <label style="background: #fbbf24; color: #ffffff; border: none; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); padding: 7px 0; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; text-align: center; cursor: pointer; display: block; width: 100%; margin: 0; line-height: 1.2;">UPLOAD<input type="file" name="gatein_invoice_att" style="display: none;" onchange="this.form.submit()"></label>
            </form>'''

        gatepass_url = reverse('gatein_pdf_download', args=[item.id])
        gatepass = f'''<div class="d-flex justify-content-center gap-1">
            <a class="btn" style="background: #fbbf24; color: white; width: 34px; height: 34px; display: inline-flex; align-items: center; justify-content: center; border-radius: 8px;" href="{gatepass_url}" target="_blank" title="Download Gate Pass">
                <i class="fas fa-luggage-cart"></i>
            </a>
        </div>'''

        data.append({
            'edit': edit_btn,
            'id': item.id,
            'gatein_created_at': item.gatein_created_at.strftime('%Y-%m-%d %H:%M:%S') if item.gatein_created_at else '',
            'gatein_pre_id': str(item.gatein_pre_id) if item.gatein_pre_id else 'None',
            'inward_pod': inward_pod,
            'gatepass': gatepass,
            'gatein_job_no': item.gatein_job_no or '',
            'gatein_invoice': item.gatein_invoice or '',
            'gatein_customer': str(item.gatein_customer) if item.gatein_customer else 'None',
            'gatein_updated_at': item.gatein_updated_at.strftime('%Y-%m-%d %H:%M:%S') if item.gatein_updated_at else '',
            'gatein_updated_by': str(item.gatein_updated_by) if item.gatein_updated_by else 'None',
            'delete': delete_btn
        })

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    })
