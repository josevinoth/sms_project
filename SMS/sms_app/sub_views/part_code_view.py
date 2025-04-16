from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from ..forms import Part_codeForm
from ..models import PkpartcodeInfo, Stockdescription

@login_required(login_url='login_page')
def part_code_add(request, pc_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    part_code = request.session.get('pc_code', None)  # Returns None if 'pc_code' doesn't exist
    part_code_list = PkpartcodeInfo.objects.all().order_by('id')
    page_number = request.GET.get('page')
    paginator = Paginator(part_code_list, 50)
    page_obj = paginator.get_page(page_number)

    if request.method == "GET":
        if pc_id == 0:
            form = Part_codeForm()
        else:
            part_code = get_object_or_404(PkpartcodeInfo, pk=pc_id)
            form = Part_codeForm(instance=part_code)
        return render(request, "asset_mgt_app/part_code_add.html", {
            'form': form,
            'user_id': user_id,
            'first_name': first_name,
            'part_code_list': part_code_list,
            'page_obj': page_obj,
            'part_code': part_code

        })

    else:
        if pc_id == 0:
            form = Part_codeForm(request.POST)
        else:
            part_code = get_object_or_404(PkpartcodeInfo, pk=pc_id)
            form = Part_codeForm(request.POST, instance=part_code)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Record Saved Successfully')
            except IntegrityError:
                messages.error(request, 'Error: Part Code must be unique.')
        else:
            messages.error(request, 'Record Not Saved Successfully. Please check for errors.')
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
                    messages.error(request, f"Error in {field}: {error}")

        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

@login_required(login_url='login_page')
def part_code_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    partcode_list = PkpartcodeInfo.objects.all().order_by('id')

    page_number = request.GET.get('page')
    paginator = Paginator(partcode_list, 50)
    page_obj = paginator.get_page(page_number)

    context = {
        'partcode_list': partcode_list,
        'page_obj': page_obj,
        'user_id': user_id,
        'first_name': first_name
    }
    return render(request, "asset_mgt_app/part_code_list.html", context)

@login_required(login_url='login_page')
def part_code_delete(request, pc_id):
    part_code = get_object_or_404(PkpartcodeInfo, pk=pc_id)
    part_code.delete()
    messages.success(request, 'Part Code deleted successfully.')
    return redirect('/SMS/part_code_list')

@login_required(login_url='login_page')
def get_stock_descriptions(request):
    query = request.GET.get('q', '')  # Get search term
    descriptions = Stockdescription.objects.filter(stock_description__icontains=query).values("id", "stock_description")

    # Ensure uniqueness in case of duplicate descriptions
    descriptions_list = list({desc["stock_description"]: desc for desc in descriptions}.values())

    return JsonResponse(descriptions_list, safe=False)

@login_required(login_url='login_page')
def get_part_code(request):
    query = request.GET.get('q', '')
    part_codes = PkpartcodeInfo.objects.filter(pc_code__icontains=query).values("id", "pc_code")

    # Remove duplicates (though pc_code is already unique by model definition)
    code_list = list({code["pc_code"]: code for code in part_codes}.values())

    return JsonResponse(code_list, safe=False)

@login_required(login_url='login_page')
def export_partcodes_excel(request):
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=PartCodes.xlsx'

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Part Codes'

    # Add headers
    headers = [
        'Part Code', 'Stock Description', 'Length', 'Width', 'Height',
        'Unit of Measure', 'Stock Type', 'Created At', 'Updated At', 'Updated By',
        'Conversion Length', 'Diameter Width'
    ]
    sheet.append(headers)

    partcodes = PkpartcodeInfo.objects.all().select_related(
        'pc_stock_description', 'pc_uom', 'pc_stock_type', 'pc_updated_by'
    )

    for pc in partcodes:
        sheet.append([
            pc.pc_code,
            pc.pc_stock_description.stock_description if pc.pc_stock_description else '',
            pc.pc_length,
            pc.pc_width,
            pc.pc_height,
            pc.pc_uom.uom_name if pc.pc_uom else '',
            pc.pc_stock_type.stock_type if pc.pc_stock_type else '',
            pc.pc_created_at.strftime('%Y-%m-%d %H:%M:%S') if pc.pc_created_at else '',
            pc.pc_updated_at.strftime('%Y-%m-%d %H:%M:%S') if pc.pc_updated_at else '',
            pc.pc_updated_by.username if pc.pc_updated_by else '',
            pc.pc_con_length,
            pc.pc_diameter_width,
        ])

    workbook.save(response)
    return response


@login_required(login_url='login_page')
def partcode_search(request):
    first_name = request.session.get('first_name')
    part_code = request.GET.get("part_code", "")  # corrected key name and default value

    part_code_list = PkpartcodeInfo.objects.filter(
        Q(pc_code__icontains=part_code)
    ).order_by('-id')

    paginator = Paginator(part_code_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'part_code_list': part_code_list,
        'first_name': first_name,
        'page_obj': page_obj,
    }
    return render(request, "asset_mgt_app/part_code_list.html", context)
