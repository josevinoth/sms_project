import base64
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa

from .dispatch_add_view import get_base64_image
from ..forms import PregateintruckForm
from ..models import Pregateintruckinfo,Gatein_pre_info,HighvalueInfo
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from ..sub_models.transporter_mod import Transporter_name

@login_required(login_url='login_page')
def pregateintruck_add(request, pregateintruck_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    gatein_num_id = request.session['gatein_num_id']
    print(gatein_num_id, 'gatein')

    high_list = HighvalueInfo.objects.filter(hc_pregatein_number_id=gatein_num_id)

    # 👉 Get the latest High Value Checklist for this Gatein (if exists)
    highvalue_instance = high_list.order_by('-id').first()
    checklist = highvalue_instance  # alias for template
    approval_status_id = None
    if highvalue_instance:
        approval_status_id = highvalue_instance.hc_approval_status_id

    if request.method == "GET":
        if pregateintruck_id == 0:
            form = PregateintruckForm()
            truck = None
            high_value_check = None
        else:
            pregateintruck = get_object_or_404(Pregateintruckinfo, pk=pregateintruck_id)
            truck = pregateintruck
            form = PregateintruckForm(instance=pregateintruck)
            request.session['ses_pregateintruck_id'] = pregateintruck_id
            high_value_check = getattr(pregateintruck, 'pregatein_high_value_id', None)

        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'gatein_num_id': gatein_num_id,
            'truck': truck,
            'high_list': high_list,
            'highvalue_instance': highvalue_instance,
            'checklist': checklist,
            'high_value_check': high_value_check,
            'approval_status_id': approval_status_id,  # ✅ add this

        }
        return render(request, "asset_mgt_app/pregateintruck_add.html", context)

    else:
        if pregateintruck_id == 0:
            form = PregateintruckForm(request.POST)
            if form.is_valid():
                pregateintruck = form.save(commit=False)

                # Process driver signature
                driver_data = request.POST.get('driver_signature_data')
                if driver_data:
                    format, imgstr = driver_data.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'driver_signature.{ext}')
                    pregateintruck.pregatein_driver_signature = data

                # Process supervisor signature
                supervisor_data = request.POST.get('supervisor_signature_data')
                if supervisor_data:
                    format, imgstr = supervisor_data.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'supervisor_signature.{ext}')
                    pregateintruck.pregatein_supervisor_signature = data

                pregateintruck.save()
                messages.success(request, 'Record Updated Successfully')
                last_id = pregateintruck.id
                pregateintruckdetails_list(request, gatein_num_id)
                return redirect('/SMS/pregateintruck_update/' + str(last_id))
            else:
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])

        else:
            pregateintruck = get_object_or_404(Pregateintruckinfo, pk=pregateintruck_id)
            form = PregateintruckForm(request.POST, instance=pregateintruck)
            if form.is_valid():
                pregateintruck = form.save(commit=False)

                # Process driver signature
                driver_data = request.POST.get('driver_signature_data')
                if driver_data:
                    format, imgstr = driver_data.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'driver_signature.{ext}')
                    pregateintruck.pregatein_driver_signature = data

                # Process supervisor signature
                supervisor_data = request.POST.get('supervisor_signature_data')
                if supervisor_data:
                    format, imgstr = supervisor_data.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'supervisor_signature.{ext}')
                    pregateintruck.pregatein_supervisor_signature = data

                pregateintruck.save()
                messages.success(request, 'Record Updated Successfully')
                pregateintruckdetails_list(request, gatein_num_id)
                return redirect(request.META['HTTP_REFERER'])
            else:
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
def pregateintruckdetails_list(request,gatein_num_id):
    turck_numbers=list(Pregateintruckinfo.objects.filter(pregatein_number=gatein_num_id).values_list('pregatein_truck_number',flat=True))
    driver_names=list(Pregateintruckinfo.objects.filter(pregatein_number=gatein_num_id).values_list('pregatein_driver',flat=True))
    pre_gatein_num=Gatein_pre_info.objects.get(id=gatein_num_id).gatein_pre_number
    Gatein_pre_info.objects.filter(gatein_pre_number=pre_gatein_num).update(gatein_pre_truck_number=turck_numbers)
    Gatein_pre_info.objects.filter(gatein_pre_number=pre_gatein_num).update(gatein_pre_driver_name=driver_names)
    return (turck_numbers,driver_names)

# List pregateintruck
@login_required(login_url='login_page')
def pregateintruck_list(request):
    first_name = request.session.get('first_name')
    Gatein_pre_list=Pregateintruckinfo.objects.all()
    page_number = request.GET.get('page')
    paginator = Paginator(Gatein_pre_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
            'page_obj' :page_obj ,
            'first_name': first_name
        }
    return render(request,"asset_mgt_app/gatein_pre_list.html",context)

#Delete pregateintruck
@login_required(login_url='login_page')
def pregateintruck_delete(request,pregateintruck_id):
    pregateintruck = Pregateintruckinfo.objects.get(pk=pregateintruck_id)
    pregateintruck.delete()
    gatein_num_id = request.session['gatein_num_id']
    pregateintruckdetails_list(request,gatein_num_id)
    return (redirect(request.META['HTTP_REFERER'])

# Cancel pregateintruck
@login_required(login_url='login_page'))
def pregateintruck_cancel(request):
    gatein_num_id = request.session['gatein_num_id']
    return redirect('/SMS/gatein_pre_update/' + str(gatein_num_id))
@csrf_exempt
def add_transporter(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            return JsonResponse({"success": False, "error": "Transporter name cannot be empty."})

        existing = Transporter_name.objects.filter(transporter_name__iexact=name).first()
        if existing:
            return JsonResponse({
                "success": False,
                "id": existing.id,
                "name": existing.transporter_name,
                "error": "This transporter already exists."
            })

        new = Transporter_name.objects.create(transporter_name=name)
        return JsonResponse({"success": True, "id": new.id, "name": new.transporter_name})

    return JsonResponse({"success": False, "error": "Invalid request"})
@login_required(login_url='login_page')
def pregatein_gatepass_pdf(request, pregatein_id=0, download=False):
    try:
        truck = get_object_or_404(Pregateintruckinfo, id=pregatein_id)

        if truck.pregatein_job_category_id == 1:
            return JsonResponse({"success": False, "error": "Gatepass PDF only available for Job Category 3."}, status=403)

        # Convert signatures to base64 strings
        truck.driver_signature_base64 = get_base64_image(truck.pregatein_driver_signature)
        truck.supervisor_signature_base64 = get_base64_image(truck.pregatein_supervisor_signature)

        context = {
            'truck': truck,
        }

        template = get_template('asset_mgt_app/pregatein_gate_pass.html')
        html = template.render(context)

        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

        if pisa_status.err:
            raise ValueError('Error generating PDF')

        pdf_buffer.seek(0)
        pdf_data = pdf_buffer.read()
        pdf_buffer.close()

        if download:
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Pregatein_Gatepass_{truck.pregatein_number}.pdf"'
            return response

        return pdf_data  # For email attachment use

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@login_required(login_url='login_page')
def pregatein_gatepass_pdf_download(request, pregatein_id):
    return pregatein_gatepass_pdf(request, pregatein_id, download=True)