import csv
import io
import json
import math
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..models import (
    CustomerBoxItemMaster,
    CustomerInfo,
    MyUser,
    Naconsumables,
    Nadimension,
    Nadimensiontype,
    Natypeofreq,
    PkBomRuleComponent,
    PkBomRuleMaster,
    PkneedassessmentInfo,
    PkpartcodeInfo,
    PkstockpurchasesInfo,
    Pkstocktype,
    Pkwooddescription,
    Unitofmeasure,
    User_extInfo,
    VehicletypeInfo,
)
from .general_utils import generate_next_number, get_branch_code, get_financial_year, get_session_branch_id


def _get_user_context(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID') or (request.user.id if request.user.is_authenticated else None)
    user_ext = User_extInfo.objects.filter(user=user_id).first() if user_id else None
    role = user_ext.emp_role if user_ext else None
    user_obj = MyUser.objects.filter(pk=user_id).first() if user_id else (request.user if request.user.is_authenticated else None)
    return first_name, user_id, role, user_obj


# ==============================================================================
# 1. CUSTOMER BOX ITEM MASTER (CRUD + TAGGING API)
# ==============================================================================

@login_required(login_url='login_page')
def customer_box_master_list(request):
    first_name, user_id, role, _ = _get_user_context(request)
    customer_id = request.GET.get('customer_id', '').strip()
    search_q = request.GET.get('q', '').strip()

    items = CustomerBoxItemMaster.objects.select_related(
        'cbm_customer', 'cbm_type_of_req', 'cbm_dimension_type', 'cbm_uom', 'cbm_consumables'
    ).prefetch_related('cbm_wood_type', 'cbm_wood_description').all()

    if customer_id:
        if customer_id == 'global':
            items = items.filter(cbm_customer__isnull=True)
        elif customer_id.isdigit():
            items = items.filter(cbm_customer_id=int(customer_id))

    if search_q:
        items = items.filter(
            Q(cbm_item_code__icontains=search_q)
            | Q(cbm_item_name__icontains=search_q)
            | Q(cbm_bvm_code__icontains=search_q)
            | Q(cbm_customer__cu_name__icontains=search_q)
        )

    context = {
        'items': items,
        'customers': CustomerInfo.objects.all().order_by('cu_name'),
        'req_types': Natypeofreq.objects.all().order_by('id'),
        'dim_types': Nadimensiontype.objects.all().order_by('id'),
        'uoms': Unitofmeasure.objects.filter(id__in=[1, 2, 3, 4]).order_by('id'),
        'wood_types': Pkstocktype.objects.filter(id__in=[1, 4]).order_by('id'),
        'wood_descs': Pkwooddescription.objects.all().order_by('id'),
        'consumables': Naconsumables.objects.all().order_by('id'),
        'vehicles': VehicletypeInfo.objects.all().order_by('id'),
        'selected_customer_id': customer_id,
        'search_q': search_q,
        'first_name': first_name,
        'role': role,
    }
    return render(request, 'asset_mgt_app/pk_customer_box_master_list.html', context)


@login_required(login_url='login_page')
def customer_box_master_save(request, pk=0):
    if request.method != 'POST':
        return redirect('customer_box_master_list')

    _, _, _, user_obj = _get_user_context(request)
    instance = get_object_or_404(CustomerBoxItemMaster, pk=pk) if pk else CustomerBoxItemMaster()

    cust_id = request.POST.get('cbm_customer') or None
    instance.cbm_customer_id = int(cust_id) if cust_id and str(cust_id).isdigit() else None
    instance.cbm_item_code = (request.POST.get('cbm_item_code') or '').strip()
    instance.cbm_item_name = (request.POST.get('cbm_item_name') or '').strip()
    instance.cbm_type_of_req_id = request.POST.get('cbm_type_of_req') or None
    instance.cbm_dimension_type_id = request.POST.get('cbm_dimension_type') or 4
    instance.cbm_uom_id = request.POST.get('cbm_uom') or None
    instance.cbm_length = float(request.POST.get('cbm_length') or 0.0)
    instance.cbm_width = float(request.POST.get('cbm_width') or 0.0)
    instance.cbm_height = float(request.POST.get('cbm_height') or 0.0)
    instance.cbm_clearance = float(request.POST.get('cbm_clearance') or 0.0)
    instance.cbm_plywood_thickness = float(request.POST.get('cbm_plywood_thickness') or 0.0)
    # Directional Clearance
    instance.cbm_clr_length = float(request.POST.get('cbm_clr_length') or 0.0)
    instance.cbm_clr_width = float(request.POST.get('cbm_clr_width') or 0.0)
    instance.cbm_clr_top = float(request.POST.get('cbm_clr_top') or 0.0)
    # Directional Thickness
    instance.cbm_thk_length = float(request.POST.get('cbm_thk_length') or 7.0)
    instance.cbm_thk_width = float(request.POST.get('cbm_thk_width') or 7.0)
    instance.cbm_thk_height = float(request.POST.get('cbm_thk_height') or 20.0)
    instance.cbm_job_weight = float(request.POST.get('cbm_job_weight') or 0.0)
    instance.cbm_consumables_id = request.POST.get('cbm_consumables') or None
    instance.cbm_vechicle_type_id = request.POST.get('cbm_vechicle_type') or None
    instance.cbm_notes = (request.POST.get('cbm_notes') or '').strip()
    instance.cbm_is_active = request.POST.get('cbm_is_active', 'on') in ('on', 'true', '1', 'True')
    instance.cbm_updated_by = user_obj

    if not instance.cbm_bvm_code:
        instance.cbm_bvm_code = generate_next_number(CustomerBoxItemMaster, 'cbm_bvm_code', 'CBM_', 5)

    instance.save()

    wood_type_ids = [int(x) for x in request.POST.getlist('cbm_wood_type') if str(x).isdigit()]
    wood_desc_ids = [int(x) for x in request.POST.getlist('cbm_wood_description') if str(x).isdigit()]
    instance.cbm_wood_type.set(wood_type_ids)
    instance.cbm_wood_description.set(wood_desc_ids)

    messages.success(request, f"Customer Box Item '{instance.cbm_item_code or instance.cbm_item_name}' saved.")
    return redirect(request.POST.get('next') or 'customer_box_master_list')


@login_required(login_url='login_page')
def customer_box_master_form_view(request, pk=0):
    """Full-page Add/Edit Customer Box Item Master form."""
    if request.method == 'POST':
        return customer_box_master_save(request, pk=pk)

    first_name, user_id, role, _ = _get_user_context(request)
    item = get_object_or_404(
        CustomerBoxItemMaster.objects.prefetch_related('cbm_wood_type', 'cbm_wood_description'), pk=pk
    ) if pk else None

    context = {
        'item': item,
        'selected_wood_type_ids': list(item.cbm_wood_type.values_list('id', flat=True)) if item else [],
        'selected_wood_desc_ids': list(item.cbm_wood_description.values_list('id', flat=True)) if item else [],
        'customers': CustomerInfo.objects.all().order_by('cu_name'),
        'req_types': Natypeofreq.objects.all().order_by('id'),
        'dim_types': Nadimensiontype.objects.all().order_by('id'),
        'uoms': Unitofmeasure.objects.filter(id__in=[1, 2, 3, 4]).order_by('id'),
        'wood_types': Pkstocktype.objects.filter(id__in=[1, 4]).order_by('id'),
        'wood_descs': Pkwooddescription.objects.all().order_by('id'),
        'consumables': Naconsumables.objects.all().order_by('id'),
        'vehicles': VehicletypeInfo.objects.all().order_by('id'),
        'first_name': first_name,
        'role': role,
    }
    return render(request, 'asset_mgt_app/pk_customer_box_master_form.html', context)


@login_required(login_url='login_page')
def customer_box_master_delete(request, pk):
    obj = get_object_or_404(CustomerBoxItemMaster, pk=pk)
    obj.delete()
    messages.success(request, "Customer Box Item deleted.")
    return redirect(request.META.get('HTTP_REFERER') or 'customer_box_master_list')


@login_required(login_url='login_page')
def api_customer_box_items(request):
    """Returns active CustomerBoxItemMaster records for a customer (+ global items) as JSON."""
    customer_id = request.GET.get('customer_id', '').strip()
    search_q = request.GET.get('q', '').strip()

    qs = CustomerBoxItemMaster.objects.filter(cbm_is_active=True).select_related(
        'cbm_customer', 'cbm_type_of_req', 'cbm_dimension_type', 'cbm_uom', 'cbm_consumables', 'cbm_vechicle_type'
    ).prefetch_related('cbm_wood_type', 'cbm_wood_description')

    if customer_id and customer_id.isdigit():
        qs = qs.filter(Q(cbm_customer_id=int(customer_id)) | Q(cbm_customer__isnull=True))

    if search_q:
        qs = qs.filter(
            Q(cbm_item_code__icontains=search_q)
            | Q(cbm_item_name__icontains=search_q)
            | Q(cbm_bvm_code__icontains=search_q)
        )

    data = []
    for item in qs[:200]:
        data.append({
            'id': item.id,
            'bvm_code': item.cbm_bvm_code or '',
            'item_code': item.cbm_item_code or '',
            'item_name': item.cbm_item_name or '',
            'customer_id': item.cbm_customer_id,
            'customer_name': item.cbm_customer.cu_name if item.cbm_customer else 'Global Standard',
            'type_of_req_id': item.cbm_type_of_req_id,
            'type_of_req': str(item.cbm_type_of_req) if item.cbm_type_of_req else '',
            'dimension_type_id': item.cbm_dimension_type_id or 4,
            'dimension_type': str(item.cbm_dimension_type) if item.cbm_dimension_type else 'Not Applicable',
            'length': item.cbm_length,
            'width': item.cbm_width,
            'height': item.cbm_height,
            'clearance': item.cbm_clearance or 0.0,
            'plywood_thickness': item.cbm_plywood_thickness or 0.0,
            'clr_length': item.cbm_clr_length,
            'clr_width': item.cbm_clr_width,
            'clr_top': item.cbm_clr_top,
            'thk_length': item.cbm_thk_length,
            'thk_width': item.cbm_thk_width,
            'thk_height': item.cbm_thk_height,
            'uom_id': item.cbm_uom_id,
            'uom': str(item.cbm_uom) if item.cbm_uom else '',
            'job_weight': item.cbm_job_weight,
            'wood_type_ids': list(item.cbm_wood_type.values_list('id', flat=True)),
            'wood_type_names': ', '.join(str(w) for w in item.cbm_wood_type.all()),
            'wood_desc_ids': list(item.cbm_wood_description.values_list('id', flat=True)),
            'consumables_id': item.cbm_consumables_id,
            'vechicle_type_id': item.cbm_vechicle_type_id,
            'notes': item.cbm_notes or '',
        })

    return JsonResponse({'status': 'success', 'items': data})


@login_required(login_url='login_page')
def api_na_tag_box_items(request):
    """Multi-select tag CustomerBoxItemMaster rows into a Need Assessment as Nadimension snapshots."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)

    assessment_id = payload.get('assessment_id') or request.session.get('na_assessment_id')
    selected_items = payload.get('items') or []
    if not assessment_id or not selected_items:
        return JsonResponse({'status': 'error', 'message': 'Missing assessment_id or items'}, status=400)

    assessment = get_object_or_404(PkneedassessmentInfo, pk=assessment_id)
    _, _, _, user_obj = _get_user_context(request)
    if not user_obj:
        user_obj = assessment.na_updated_by

    fy = get_financial_year()
    branch_id = get_session_branch_id(request)
    branch_code = get_branch_code(branch_id)
    prefix = f"{fy}_{branch_code}_ITM_"

    created_ids = []
    with transaction.atomic():
        for entry in selected_items:
            master_id = entry.get('master_id')
            qty = int(entry.get('quantity') or 1)
            if not master_id or qty <= 0:
                continue
            master = CustomerBoxItemMaster.objects.filter(pk=master_id).first()
            if not master:
                continue

            req_type = master.cbm_type_of_req or Natypeofreq.objects.first()
            if not req_type:
                continue

            next_item_num = generate_next_number(Nadimension, 'nad_item', prefix, 6)
            part_label = f"{master.cbm_item_code} - {master.cbm_item_name}".strip(' -')

            nad = Nadimension.objects.create(
                nad_assess_num=assessment,
                nad_item=next_item_num,
                nad_length=master.cbm_length,
                nad_width=master.cbm_width,
                nad_height=master.cbm_height,
                nad_quantity=qty,
                nad_updated_by=user_obj,
                nad_job_weight=master.cbm_job_weight,
                nad_type_of_req=req_type,
                nad_uom=master.cbm_uom,
                nad_plywood_thickness=master.cbm_plywood_thickness or 0.0,
                nad_clearance=master.cbm_clearance if master.cbm_clearance is not None else 0.0,
                nad_clr_length=master.cbm_clr_length,
                nad_clr_width=master.cbm_clr_width,
                nad_clr_top=master.cbm_clr_top,
                nad_thk_length=master.cbm_thk_length,
                nad_thk_width=master.cbm_thk_width,
                nad_thk_height=master.cbm_thk_height,
                nad_dimension_type=master.cbm_dimension_type or Nadimensiontype.objects.filter(pk=4).first(),
                nad_consumables=master.cbm_consumables,
                nad_vechicle_type=master.cbm_vechicle_type,
                nad_master_item=master,
                nad_customer_part_code=part_label[:120],
            )
            nad.nad_wood_type.set(master.cbm_wood_type.all())
            nad.nad_wood_description.set(master.cbm_wood_description.all())
            created_ids.append(nad.id)

    return JsonResponse({'status': 'success', 'created_count': len(created_ids), 'created_ids': created_ids})


# ==============================================================================
# 2. AUTO-BOM ENGINEERING RULE MATRIX (SIZE x WEIGHT KG)
# ==============================================================================

DEFAULT_WEIGHT_TIERS = [
    # (min_kg, max_kg, runner_w, runner_h, runner_pitch_ft, lift_w, lift_h, ply_mm, frame_w, frame_h, batten_pitch_ft, heavy_bracing, nail_cft, nail_100sqft)
    (0, 500, 3.0, 3.0, 2.5, 3.0, 1.5, 8.0, 3.0, 1.0, 2.5, False, 0.35, 0.25),
    (501, 1000, 3.0, 4.0, 2.0, 4.0, 1.5, 10.0, 4.0, 1.0, 2.0, False, 0.40, 0.30),
    (1001, 3000, 4.0, 4.0, 1.8, 4.0, 1.5, 12.0, 4.0, 1.0, 2.0, False, 0.45, 0.35),
    (3001, 5000, 4.0, 4.0, 1.5, 4.0, 2.0, 12.0, 4.0, 1.5, 1.75, True, 0.50, 0.40),
    (5001, 10000, 4.0, 5.0, 1.35, 5.0, 2.0, 15.0, 4.0, 1.5, 1.5, True, 0.55, 0.45),
    (10001, 15000, 5.0, 5.0, 1.25, 6.0, 2.0, 18.0, 4.0, 2.0, 1.5, True, 0.60, 0.50),
    (15001, 20000, 6.0, 4.0, 1.15, 6.0, 2.5, 18.0, 4.0, 2.0, 1.25, True, 0.65, 0.55),
]

DEFAULT_SIZE_TIERS_M = [
    (1.0, 1.0, 1.0, 'Up to 1x1x1m'),
    (2.0, 2.0, 2.0, 'Up to 2x2x2m'),
    (3.0, 3.0, 3.0, 'Up to 3x3x3m'),
    (4.0, 4.0, 4.0, 'Up to 4x4x4m'),
    (99.0, 99.0, 99.0, 'Oversize (>4m)'),
]


def seed_default_bom_rules(user=None, force=False):
    if not force and PkBomRuleMaster.objects.exists():
        return 0
    if force:
        PkBomRuleMaster.objects.all().delete()

    created = 0
    priority = 10
    for max_l, max_w, max_h, size_label in DEFAULT_SIZE_TIERS_M:
        for (min_kg, max_kg, rw, rh, r_pitch, lw, lh, ply_mm, fw, fh, b_pitch, heavy, ncft, nsqft) in DEFAULT_WEIGHT_TIERS:
            # Larger spans (>2m) bump batten tightness slightly
            adj_batten_pitch = max(1.0, round(b_pitch - (0.15 if max_l >= 3.0 and max_l < 99 else 0.0), 2))
            PkBomRuleMaster.objects.create(
                br_name=f"{size_label} | {min_kg}-{max_kg} kg",
                br_template_type='all',
                br_max_length_m=max_l,
                br_max_width_m=max_w,
                br_max_height_m=max_h,
                br_min_weight_kg=min_kg,
                br_max_weight_kg=max_kg,
                br_base_runner_w_in=rw,
                br_base_runner_h_in=rh,
                br_base_runner_pitch_ft=r_pitch,
                br_lifting_runner_w_in=lw,
                br_lifting_runner_h_in=lh,
                br_lifting_runner_nos=3 if max_l >= 3.0 and min_kg >= 5000 else 2,
                br_deck_mat='plywood',
                br_deck_thickness=ply_mm,
                br_wall_ply_mm=ply_mm,
                br_frame_w_in=fw,
                br_frame_h_in=fh,
                br_batten_pitch_ft=adj_batten_pitch,
                br_mid_rail_height_ft=4.0,
                br_top_cross_width_ft=3.5,
                br_support_w_in=3.0 if min_kg <= 3000 else 4.0,
                br_support_h_in=1.0 if min_kg <= 3000 else 1.5,
                br_arrest_w_in=4.0,
                br_arrest_h_in=2.0 if min_kg <= 5000 else 3.0,
                br_heavy_bracing=heavy,
                br_nail_kg_per_cft=ncft,
                br_nail_kg_per_100sqft=nsqft,
                br_vci_overlap_pct=15.0,
                br_strapping_pitch_ft=2.5 if min_kg <= 3000 else 2.0,
                br_priority=priority,
                br_is_active=True,
                br_updated_by=user,
            )
            created += 1
            priority += 10
    return created


@login_required(login_url='login_page')
def bom_rule_master_list(request):
    first_name, user_id, role, user_obj = _get_user_context(request)
    if request.GET.get('reset_defaults') == '1':
        cnt = seed_default_bom_rules(user=user_obj, force=True)
        messages.success(request, f"Reset {cnt} default Size x Weight (KG) BOM engineering rules.")
        return redirect('bom_rule_master_list')

    if not PkBomRuleMaster.objects.exists():
        seed_default_bom_rules(user=user_obj, force=False)

    size_filter = request.GET.get('size_m', '').strip()
    rules = PkBomRuleMaster.objects.select_related('br_req_type').all()
    if size_filter:
        try:
            rules = rules.filter(br_max_length_m=float(size_filter))
        except ValueError:
            pass

    context = {
        'rules': rules,
        'req_types': Natypeofreq.objects.all().order_by('id'),
        'size_filter': size_filter,
        'first_name': first_name,
        'role': role,
    }
    return render(request, 'asset_mgt_app/pk_bom_rule_master.html', context)


@login_required(login_url='login_page')
def bom_rule_master_save(request, pk=0):
    if request.method != 'POST':
        return redirect('bom_rule_master_list')

    _, _, _, user_obj = _get_user_context(request)
    rule = get_object_or_404(PkBomRuleMaster, pk=pk) if pk else PkBomRuleMaster()

    rule.br_name = (request.POST.get('br_name') or 'Custom Rule').strip()
    rule.br_req_type_id = request.POST.get('br_req_type') or None
    rule.br_template_type = request.POST.get('br_template_type') or 'all'
    rule.br_max_length_m = float(request.POST.get('br_max_length_m') or 4.0)
    rule.br_max_width_m = float(request.POST.get('br_max_width_m') or 4.0)
    rule.br_max_height_m = float(request.POST.get('br_max_height_m') or 4.0)
    rule.br_min_weight_kg = float(request.POST.get('br_min_weight_kg') or 0.0)
    rule.br_max_weight_kg = float(request.POST.get('br_max_weight_kg') or 500.0)

    rule.br_base_runner_w_in = float(request.POST.get('br_base_runner_w_in') or 3.0)
    rule.br_base_runner_h_in = float(request.POST.get('br_base_runner_h_in') or 4.0)
    rule.br_base_runner_pitch_ft = float(request.POST.get('br_base_runner_pitch_ft') or 2.0)
    rule.br_lifting_runner_w_in = float(request.POST.get('br_lifting_runner_w_in') or 4.0)
    rule.br_lifting_runner_h_in = float(request.POST.get('br_lifting_runner_h_in') or 1.5)
    rule.br_lifting_runner_nos = int(request.POST.get('br_lifting_runner_nos') or 2)
    rule.br_deck_mat = request.POST.get('br_deck_mat') or 'plywood'
    rule.br_deck_thickness = float(request.POST.get('br_deck_thickness') or 10.0)

    rule.br_wall_ply_mm = float(request.POST.get('br_wall_ply_mm') or 10.0)
    rule.br_frame_w_in = float(request.POST.get('br_frame_w_in') or 4.0)
    rule.br_frame_h_in = float(request.POST.get('br_frame_h_in') or 1.0)
    rule.br_batten_pitch_ft = float(request.POST.get('br_batten_pitch_ft') or 2.0)
    rule.br_mid_rail_height_ft = float(request.POST.get('br_mid_rail_height_ft') or 4.0)
    rule.br_top_cross_width_ft = float(request.POST.get('br_top_cross_width_ft') or 3.5)

    rule.br_support_w_in = float(request.POST.get('br_support_w_in') or 3.0)
    rule.br_support_h_in = float(request.POST.get('br_support_h_in') or 1.0)
    rule.br_arrest_w_in = float(request.POST.get('br_arrest_w_in') or 4.0)
    rule.br_arrest_h_in = float(request.POST.get('br_arrest_h_in') or 2.0)
    rule.br_heavy_bracing = request.POST.get('br_heavy_bracing') in ('on', 'true', '1', 'True')

    rule.br_nail_kg_per_cft = float(request.POST.get('br_nail_kg_per_cft') or 0.45)
    rule.br_nail_kg_per_100sqft = float(request.POST.get('br_nail_kg_per_100sqft') or 0.35)
    rule.br_vci_overlap_pct = float(request.POST.get('br_vci_overlap_pct') or 15.0)
    rule.br_strapping_pitch_ft = float(request.POST.get('br_strapping_pitch_ft') or 2.5)
    rule.br_priority = int(request.POST.get('br_priority') or 100)
    rule.br_is_active = request.POST.get('br_is_active', 'on') in ('on', 'true', '1', 'True')
    rule.br_updated_by = user_obj
    rule.save()

    messages.success(request, f"BOM Rule '{rule.br_name}' saved.")
    return redirect('bom_rule_master_list')


@login_required(login_url='login_page')
def bom_rule_master_delete(request, pk):
    obj = get_object_or_404(PkBomRuleMaster, pk=pk)
    obj.delete()
    messages.success(request, "BOM Rule deleted.")
    return redirect('bom_rule_master_list')


def _default_components_for_rule(rule):
    """Build default component terminology rows from rule summary fields."""
    rw = rule.br_base_runner_w_in if rule else 3.0
    rh = rule.br_base_runner_h_in if rule else 4.0
    rpitch = rule.br_base_runner_pitch_ft if rule else 2.0
    lw = rule.br_lifting_runner_w_in if rule else 4.0
    lh = rule.br_lifting_runner_h_in if rule else 1.5
    lnos = rule.br_lifting_runner_nos if rule else 2
    dmat = rule.br_deck_mat if rule else 'plywood'
    dthk = rule.br_deck_thickness if rule else 10.0
    ply = rule.br_wall_ply_mm if rule else 10.0
    fw = rule.br_frame_w_in if rule else 4.0
    fh = rule.br_frame_h_in if rule else 1.0
    bpitch = rule.br_batten_pitch_ft if rule else 2.0
    sw = rule.br_support_w_in if rule else 3.0
    sh = rule.br_support_h_in if rule else 1.0
    aw = rule.br_arrest_w_in if rule else 4.0
    ah = rule.br_arrest_h_in if rule else 2.0
    heavy = rule.br_heavy_bracing if rule else False

    rows = [
        {'section': 'BASE', 'name': 'BASE RUNNER', 'mat': 'wood', 'len_mode': 'W_FT', 'len_val': 0, 'width_mode': 'FIXED', 'width_val': rw, 'thk_val': rh, 'qty_mode': 'PITCH_L', 'qty_val': rpitch},
        {'section': 'BASE', 'name': 'LIFTING RUNNER', 'mat': 'wood', 'len_mode': 'L_FT', 'len_val': 0, 'width_mode': 'FIXED', 'width_val': lw, 'thk_val': lh, 'qty_mode': 'FIXED', 'qty_val': lnos},
        {'section': 'BASE', 'name': 'DECK BOARD', 'mat': dmat, 'len_mode': 'L_FT', 'len_val': 0, 'width_mode': 'W_FT', 'width_val': 0, 'thk_val': dthk, 'qty_mode': 'FIXED', 'qty_val': 1},
        {'section': 'LENGTH (2 SIDES)', 'name': 'LENGTH PANEL', 'mat': 'plywood', 'len_mode': 'L_FT', 'len_val': 0, 'width_mode': 'H_FT', 'width_val': 0, 'thk_val': ply, 'qty_mode': 'FIXED', 'qty_val': 2},
        {'section': 'LENGTH (2 SIDES)', 'name': 'LENGTH FRAME (HORIZ)', 'mat': 'wood', 'len_mode': 'L_FT', 'len_val': 0, 'width_mode': 'FIXED', 'width_val': fw, 'thk_val': fh, 'qty_mode': 'FIXED', 'qty_val': 4},
        {'section': 'LENGTH (2 SIDES)', 'name': 'HEIGHT FRAME (VERT)', 'mat': 'wood', 'len_mode': 'H_FT', 'len_val': 0, 'width_mode': 'FIXED', 'width_val': fw, 'thk_val': fh, 'qty_mode': 'PITCH_L_2S', 'qty_val': bpitch},
        {'section': 'WIDTH (2 SIDES)', 'name': 'WIDTH PANEL', 'mat': 'plywood', 'len_mode': 'W_FT', 'len_val': 0, 'width_mode': 'H_FT', 'width_val': 0, 'thk_val': ply, 'qty_mode': 'FIXED', 'qty_val': 2},
        {'section': 'WIDTH (2 SIDES)', 'name': 'WIDTH FRAME (HORIZ)', 'mat': 'wood', 'len_mode': 'W_FT', 'len_val': 0, 'width_mode': 'FIXED', 'width_val': fw, 'thk_val': fh, 'qty_mode': 'FIXED', 'qty_val': 4},
        {'section': 'WIDTH (2 SIDES)', 'name': 'HEIGHT FRAME (VERT)', 'mat': 'wood', 'len_mode': 'H_FT', 'len_val': 0, 'width_mode': 'FIXED', 'width_val': fw, 'thk_val': fh, 'qty_mode': 'PITCH_W_2S', 'qty_val': bpitch},
        {'section': 'TOP', 'name': 'TOP PANEL', 'mat': 'plywood', 'len_mode': 'L_FT', 'len_val': 0, 'width_mode': 'W_FT', 'width_val': 0, 'thk_val': ply, 'qty_mode': 'FIXED', 'qty_val': 1},
        {'section': 'TOP', 'name': 'TOP LENGTH FRAME', 'mat': 'wood', 'len_mode': 'L_FT', 'len_val': 0, 'width_mode': 'FIXED', 'width_val': fw, 'thk_val': fh, 'qty_mode': 'FIXED', 'qty_val': 2},
        {'section': 'TOP', 'name': 'TOP WIDTH FRAME', 'mat': 'wood', 'len_mode': 'W_FT', 'len_val': 0, 'width_mode': 'FIXED', 'width_val': fw, 'thk_val': fh, 'qty_mode': 'FIXED', 'qty_val': 4},
        {'section': 'SUPPORTS & ARREST', 'name': 'FRAME SUPPORT (LENGTH)', 'mat': 'wood', 'len_mode': 'L_FT', 'len_val': 0, 'width_mode': 'FIXED', 'width_val': sw, 'thk_val': sh, 'qty_mode': 'FIXED', 'qty_val': 2},
        {'section': 'SUPPORTS & ARREST', 'name': 'FRAME SUPPORT (WIDTH)', 'mat': 'wood', 'len_mode': 'W_FT', 'len_val': 0, 'width_mode': 'FIXED', 'width_val': sw, 'thk_val': sh, 'qty_mode': 'FIXED', 'qty_val': 2},
        {'section': 'SUPPORTS & ARREST', 'name': 'JOB & TOP ARREST', 'mat': 'wood', 'len_mode': 'W_FT', 'len_val': 0, 'width_mode': 'FIXED', 'width_val': aw, 'thk_val': ah, 'qty_mode': 'FIXED', 'qty_val': 4 if heavy else 2},
    ]
    if heavy:
        rows.append({'section': 'SUPPORTS & ARREST', 'name': 'HEAVY DIAGONAL BRACING', 'mat': 'wood', 'len_mode': 'DIAG_LH_FT', 'len_val': 0, 'width_mode': 'FIXED', 'width_val': fw, 'thk_val': fh, 'qty_mode': 'FIXED', 'qty_val': 4})
    return rows


@login_required(login_url='login_page')
def bom_rule_form_view(request, pk=0):
    """Full-page Add/Edit BOM Rule form with dynamic Component/Terminology rows."""
    first_name, user_id, role, user_obj = _get_user_context(request)
    rule = get_object_or_404(PkBomRuleMaster, pk=pk) if pk else None

    if request.method == 'POST':
        if not rule:
            rule = PkBomRuleMaster()
        rule.br_name = (request.POST.get('br_name') or 'Custom Rule').strip()
        rule.br_req_type_id = request.POST.get('br_req_type') or None
        rule.br_template_type = request.POST.get('br_template_type') or 'all'
        rule.br_max_length_m = float(request.POST.get('br_max_length_m') or 4.0)
        rule.br_max_width_m = float(request.POST.get('br_max_width_m') or 4.0)
        rule.br_max_height_m = float(request.POST.get('br_max_height_m') or 4.0)
        rule.br_min_weight_kg = float(request.POST.get('br_min_weight_kg') or 0.0)
        rule.br_max_weight_kg = float(request.POST.get('br_max_weight_kg') or 500.0)
        rule.br_nail_kg_per_cft = float(request.POST.get('br_nail_kg_per_cft') or 0.45)
        rule.br_nail_kg_per_100sqft = float(request.POST.get('br_nail_kg_per_100sqft') or 0.35)
        rule.br_vci_overlap_pct = float(request.POST.get('br_vci_overlap_pct') or 15.0)
        rule.br_strapping_pitch_ft = float(request.POST.get('br_strapping_pitch_ft') or 2.5)
        rule.br_heavy_bracing = request.POST.get('br_heavy_bracing') in ('on', 'true', '1', 'True')
        rule.br_priority = int(request.POST.get('br_priority') or 10)
        rule.br_is_active = request.POST.get('br_is_active', 'on') in ('on', 'true', '1', 'True')
        rule.br_updated_by = user_obj

        # Sync summary runner/ply from components if provided
        sections = request.POST.getlist('comp_section[]')
        names = request.POST.getlist('comp_name[]')
        mats = request.POST.getlist('comp_mat[]')
        len_modes = request.POST.getlist('comp_len_mode[]')
        len_vals = request.POST.getlist('comp_len_val[]')
        width_modes = request.POST.getlist('comp_width_mode[]')
        width_vals = request.POST.getlist('comp_width_val[]')
        thk_vals = request.POST.getlist('comp_thk_val[]')
        qty_modes = request.POST.getlist('comp_qty_mode[]')
        qty_vals = request.POST.getlist('comp_qty_val[]')

        for i, nm in enumerate(names):
            nm_up = (nm or '').strip().upper()
            if 'BASE RUNNER' in nm_up:
                rule.br_base_runner_w_in = float(width_vals[i] or 3.0)
                rule.br_base_runner_h_in = float(thk_vals[i] or 4.0)
            elif 'PANEL' in nm_up and (mats[i] if i < len(mats) else '') == 'plywood':
                rule.br_wall_ply_mm = float(thk_vals[i] or 10.0)

        with transaction.atomic():
            rule.save()
            rule.components.all().delete()
            for i in range(len(names)):
                comp_name = (names[i] or '').strip()
                if not comp_name:
                    continue
                PkBomRuleComponent.objects.create(
                    brc_rule=rule,
                    brc_section=sections[i] if i < len(sections) else 'BASE',
                    brc_name=comp_name,
                    brc_mat=mats[i] if i < len(mats) else 'wood',
                    brc_len_mode=len_modes[i] if i < len(len_modes) else 'L_FT',
                    brc_len_val=float(len_vals[i] or 0.0) if i < len(len_vals) else 0.0,
                    brc_width_mode=width_modes[i] if i < len(width_modes) else 'FIXED',
                    brc_width_val=float(width_vals[i] or 0.0) if i < len(width_vals) else 0.0,
                    brc_thk_val=float(thk_vals[i] or 1.0) if i < len(thk_vals) else 1.0,
                    brc_qty_mode=qty_modes[i] if i < len(qty_modes) else 'FIXED',
                    brc_qty_val=float(qty_vals[i] or 1.0) if i < len(qty_vals) else 1.0,
                    brc_order=(i + 1) * 10,
                )

        messages.success(request, f"BOM Rule '{rule.br_name}' saved with {rule.components.count()} components.")
        return redirect('bom_rule_master_list')

    if rule and rule.components.exists():
        components = [
            {
                'section': c.brc_section, 'name': c.brc_name, 'mat': c.brc_mat,
                'len_mode': c.brc_len_mode, 'len_val': c.brc_len_val,
                'width_mode': c.brc_width_mode, 'width_val': c.brc_width_val,
                'thk_val': c.brc_thk_val, 'qty_mode': c.brc_qty_mode, 'qty_val': c.brc_qty_val,
            }
            for c in rule.components.all()
        ]
    else:
        components = _default_components_for_rule(rule)

    context = {
        'rule': rule,
        'components': components,
        'req_types': Natypeofreq.objects.all().order_by('id'),
        'section_choices': PkBomRuleComponent.SECTION_CHOICES,
        'len_choices': PkBomRuleComponent.LEN_MODE_CHOICES,
        'width_choices': PkBomRuleComponent.WIDTH_MODE_CHOICES,
        'qty_choices': PkBomRuleComponent.QTY_MODE_CHOICES,
        'first_name': first_name,
        'role': role,
    }
    return render(request, 'asset_mgt_app/pk_bom_rule_form.html', context)


@login_required(login_url='login_page')
def bom_rule_master_import_csv(request):
    """Import Size (MTR) x Weight (KG) BOM rules from CSV."""
    if request.method != 'POST' or not request.FILES.get('csv_file'):
        messages.error(request, "Please upload a valid CSV file.")
        return redirect('bom_rule_master_list')

    _, _, _, user_obj = _get_user_context(request)
    raw = request.FILES['csv_file'].read().decode('utf-8-sig', errors='ignore')
    reader = csv.DictReader(io.StringIO(raw))
    count = 0
    for row in reader:
        try:
            PkBomRuleMaster.objects.create(
                br_name=row.get('name') or f"{row.get('max_l_m', 4)}m | {row.get('min_kg', 0)}-{row.get('max_kg', 500)}kg",
                br_max_length_m=float(row.get('max_l_m') or 4.0),
                br_max_width_m=float(row.get('max_w_m') or 4.0),
                br_max_height_m=float(row.get('max_h_m') or 4.0),
                br_min_weight_kg=float(row.get('min_kg') or 0.0),
                br_max_weight_kg=float(row.get('max_kg') or 500.0),
                br_base_runner_w_in=float(row.get('runner_w_in') or 3.0),
                br_base_runner_h_in=float(row.get('runner_h_in') or 4.0),
                br_base_runner_pitch_ft=float(row.get('runner_pitch_ft') or 2.0),
                br_lifting_runner_w_in=float(row.get('lift_w_in') or 4.0),
                br_lifting_runner_h_in=float(row.get('lift_h_in') or 1.5),
                br_wall_ply_mm=float(row.get('ply_mm') or 10.0),
                br_deck_thickness=float(row.get('ply_mm') or 10.0),
                br_frame_w_in=float(row.get('frame_w_in') or 4.0),
                br_frame_h_in=float(row.get('frame_h_in') or 1.0),
                br_batten_pitch_ft=float(row.get('batten_pitch_ft') or 2.0),
                br_heavy_bracing=str(row.get('heavy_bracing', '')).lower() in ('1', 'true', 'yes'),
                br_updated_by=user_obj,
            )
            count += 1
        except Exception:
            continue

    messages.success(request, f"Imported {count} BOM rules from CSV.")
    return redirect('bom_rule_master_list')


def _derive_part_code(mat, h_val, w_val, l_ft):
    if mat == 'wood':
        return f"K{int(round(h_val * 10))}{int(round(w_val * 10))}{int(round(l_ft * 10))}"
    mm = int(round(h_val))
    # Map standard plywood thicknesses if available
    if mm == 10:
        return 'PY1410'
    return f"PY14{mm:02d}"


def _lookup_part_rate(part_code, fallback_rate=0.0):
    pc = PkpartcodeInfo.objects.filter(pc_code=part_code).select_related('pc_stock_description').first()
    if pc and pc.pc_stock_description:
        sp = PkstockpurchasesInfo.objects.filter(sp_stock_description=pc.pc_stock_description).order_by('-id').first()
        if sp and sp.sp_rate:
            return pc.pc_code, float(sp.sp_rate)
    return part_code, fallback_rate


def _match_bom_rule(l_m, w_m, h_m, weight_kg, template_type='plywood_box', req_type_id=None):
    if not PkBomRuleMaster.objects.exists():
        seed_default_bom_rules()

    base_qs = PkBomRuleMaster.objects.filter(br_is_active=True)
    if template_type and template_type != 'all':
        typed = base_qs.filter(Q(br_template_type=template_type) | Q(br_template_type='all'))
        if typed.exists():
            base_qs = typed

    if req_type_id:
        req_qs = base_qs.filter(Q(br_req_type_id=req_type_id) | Q(br_req_type__isnull=True))
        if req_qs.exists():
            base_qs = req_qs

    # 1. Exact Size + Weight match (ceiling on L, W, H)
    match = (
        base_qs.filter(
            br_max_length_m__gte=l_m,
            br_max_width_m__gte=w_m,
            br_max_height_m__gte=h_m,
            br_min_weight_kg__lte=weight_kg,
            br_max_weight_kg__gte=weight_kg,
        )
        .order_by('br_max_length_m', 'br_max_width_m', 'br_max_height_m', 'br_priority')
        .first()
    )
    if match:
        return match

    # 2. Match weight bracket with largest available size bracket
    match = (
        base_qs.filter(br_min_weight_kg__lte=weight_kg, br_max_weight_kg__gte=weight_kg)
        .order_by('-br_max_length_m', 'br_priority')
        .first()
    )
    if match:
        return match

    # 3. Over-weight fallback (>20,000 kg -> pick heaviest rule for the size)
    return (
        base_qs.filter(br_max_length_m__gte=l_m, br_max_width_m__gte=w_m, br_max_height_m__gte=h_m)
        .order_by('-br_max_weight_kg', 'br_max_length_m')
        .first()
        or base_qs.order_by('-br_max_weight_kg', '-br_max_length_m').first()
    )


@login_required(login_url='login_page')
def api_auto_generate_bom(request):
    """Generates structural Wood/Plywood BOM + Nails + Consumables from Box Size (cm) & Weight (kg)."""
    try:
        if request.method == 'POST':
            payload = json.loads(request.body.decode('utf-8'))
        else:
            payload = request.GET

        l_cm = float(payload.get('l_cm') or 0.0)
        w_cm = float(payload.get('w_cm') or 0.0)
        h_cm = float(payload.get('h_cm') or 0.0)
        weight_kg = float(payload.get('weight_kg') or 0.0)
        template_type = (payload.get('template_type') or 'plywood_box').strip()
        req_type_id = payload.get('req_type_id') or None
        wood_rate = float(payload.get('wood_rate') or 0.0)
        ply_rate = float(payload.get('ply_rate') or 0.0)
    except Exception as exc:
        return JsonResponse({'status': 'error', 'message': str(exc)}, status=400)

    if l_cm <= 0 or w_cm <= 0 or h_cm <= 0:
        return JsonResponse({'status': 'error', 'message': 'Box L, W, H must be greater than 0.'}, status=400)

    l_m, w_m, h_m = l_cm / 100.0, w_cm / 100.0, h_cm / 100.0
    l_ft = round(l_cm / 30.48, 2)
    w_ft = round(w_cm / 30.48, 2)
    h_ft = round(h_cm / 30.48, 2)

    rule = _match_bom_rule(l_m, w_m, h_m, weight_kg, template_type=template_type, req_type_id=req_type_id)
    if not rule:
        return JsonResponse({'status': 'error', 'message': 'No matching BOM rule found.'}, status=404)

    is_skid_only = template_type == 'skid_base'
    is_pine_ply = template_type == 'pine_ply_box'

    # Dynamic span counts
    runner_nos = max(3, math.ceil(l_ft / max(rule.br_base_runner_pitch_ft, 0.5)) + 1)
    l_batten_nos = max(2, math.ceil(l_ft / max(rule.br_batten_pitch_ft, 0.5)) + 1) * 2
    w_batten_nos = max(2, math.ceil(w_ft / max(rule.br_batten_pitch_ft, 0.5)) + 1) * 2
    deck_mat = 'wood' if is_pine_ply else rule.br_deck_mat
    deck_h = 1.0 if deck_mat == 'wood' else rule.br_deck_thickness

    def make_row(section, sec_class, name, mat, l_val, w_val, h_val, nos):
        pcode = _derive_part_code(mat, h_val, w_val, l_val)
        fallback = ply_rate if mat == 'plywood' else wood_rate
        resolved_code, resolved_rate = _lookup_part_rate(pcode, fallback)
        if not resolved_rate:
            resolved_rate = fallback
        return {
            'section': section,
            'secClass': sec_class,
            'name': name,
            'part_code': resolved_code,
            'grn': '',
            'stock_purchase_id': '',
            'mat': mat,
            'l': round(float(l_val), 2),
            'w': round(float(w_val), 2),
            'h': round(float(h_val), 2),
            'nos': int(nos),
            'rate': round(float(resolved_rate), 2),
        }

    sec_class_map = {
        'BASE': 'sec-base',
        'LENGTH (2 SIDES)': 'sec-length',
        'WIDTH (2 SIDES)': 'sec-width',
        'TOP': 'sec-top',
        'SUPPORTS & ARREST': 'sec-supports',
    }

    if rule.components.exists():
        rows = []
        for c in rule.components.all():
            if is_skid_only and c.brc_section != 'BASE':
                continue
            if c.brc_len_mode == 'L_FT':
                c_l = l_ft
            elif c.brc_len_mode == 'W_FT':
                c_l = w_ft
            elif c.brc_len_mode == 'H_FT':
                c_l = h_ft
            elif c.brc_len_mode == 'DIAG_LH_FT':
                c_l = round(math.hypot(l_ft, h_ft), 2)
            else:
                c_l = c.brc_len_val or l_ft

            if c.brc_width_mode == 'W_FT':
                c_w = w_ft
            elif c.brc_width_mode == 'H_FT':
                c_w = h_ft
            else:
                c_w = c.brc_width_val

            if c.brc_qty_mode == 'PITCH_L':
                c_nos = max(3, math.ceil(l_ft / max(c.brc_qty_val, 0.5)) + 1)
            elif c.brc_qty_mode == 'PITCH_W':
                c_nos = max(3, math.ceil(w_ft / max(c.brc_qty_val, 0.5)) + 1)
            elif c.brc_qty_mode == 'PITCH_L_2S':
                c_nos = max(2, math.ceil(l_ft / max(c.brc_qty_val, 0.5)) + 1) * 2
            elif c.brc_qty_mode == 'PITCH_W_2S':
                c_nos = max(2, math.ceil(w_ft / max(c.brc_qty_val, 0.5)) + 1) * 2
            else:
                c_nos = max(1, int(round(c.brc_qty_val or 1)))

            rows.append(make_row(
                c.brc_section,
                sec_class_map.get(c.brc_section, 'sec-base'),
                c.brc_name,
                c.brc_mat,
                c_l,
                c_w,
                c.brc_thk_val,
                c_nos,
            ))
    else:
        rows = [
            make_row('BASE', 'sec-base', 'BASE RUNNER', 'wood', w_ft, rule.br_base_runner_w_in, rule.br_base_runner_h_in, runner_nos),
            make_row('BASE', 'sec-base', 'LIFTING RUNNER', 'wood', l_ft, rule.br_lifting_runner_w_in, rule.br_lifting_runner_h_in, rule.br_lifting_runner_nos),
            make_row('BASE', 'sec-base', 'DECK BOARD', deck_mat, l_ft, w_ft, deck_h, 1),
        ]

        if not is_skid_only:
            # LENGTH (2 SIDES)
            l_horiz_nos = 6 if h_ft > rule.br_mid_rail_height_ft else 4
            rows.extend([
                make_row('LENGTH (2 SIDES)', 'sec-length', 'LENGTH PANEL', 'plywood', l_ft, h_ft, rule.br_wall_ply_mm, 2),
                make_row('LENGTH (2 SIDES)', 'sec-length', 'LENGTH FRAME (HORIZ)', 'wood', l_ft, rule.br_frame_w_in, rule.br_frame_h_in, l_horiz_nos),
                make_row('LENGTH (2 SIDES)', 'sec-length', 'HEIGHT FRAME (VERT)', 'wood', h_ft, rule.br_frame_w_in, rule.br_frame_h_in, l_batten_nos),
            ])

            # WIDTH (2 SIDES)
            w_horiz_nos = 6 if h_ft > rule.br_mid_rail_height_ft else 4
            rows.extend([
                make_row('WIDTH (2 SIDES)', 'sec-width', 'WIDTH PANEL', 'plywood', w_ft, h_ft, rule.br_wall_ply_mm, 2),
                make_row('WIDTH (2 SIDES)', 'sec-width', 'WIDTH FRAME (HORIZ)', 'wood', w_ft, rule.br_frame_w_in, rule.br_frame_h_in, w_horiz_nos),
                make_row('WIDTH (2 SIDES)', 'sec-width', 'HEIGHT FRAME (VERT)', 'wood', h_ft, rule.br_frame_w_in, rule.br_frame_h_in, w_batten_nos),
            ])

            # TOP
            top_cross_nos = max(4, math.ceil(l_ft / max(rule.br_batten_pitch_ft, 0.5)) + 1) if w_ft > rule.br_top_cross_width_ft else 4
            rows.extend([
                make_row('TOP', 'sec-top', 'TOP PANEL', 'plywood', l_ft, w_ft, rule.br_wall_ply_mm, 1),
                make_row('TOP', 'sec-top', 'TOP LENGTH FRAME', 'wood', l_ft, rule.br_frame_w_in, rule.br_frame_h_in, 2),
                make_row('TOP', 'sec-top', 'TOP WIDTH FRAME', 'wood', w_ft, rule.br_frame_w_in, rule.br_frame_h_in, top_cross_nos),
            ])

            # SUPPORTS & ARREST
            rows.extend([
                make_row('SUPPORTS & ARREST', 'sec-supports', 'FRAME SUPPORT (LENGTH)', 'wood', l_ft, rule.br_support_w_in, rule.br_support_h_in, 2),
                make_row('SUPPORTS & ARREST', 'sec-supports', 'FRAME SUPPORT (WIDTH)', 'wood', w_ft, rule.br_support_w_in, rule.br_support_h_in, 2),
                make_row('SUPPORTS & ARREST', 'sec-supports', 'JOB & TOP ARREST', 'wood', w_ft, rule.br_arrest_w_in, rule.br_arrest_h_in, 4 if rule.br_heavy_bracing else 2),
            ])
            if rule.br_heavy_bracing:
                diag_ft = round(math.hypot(l_ft, h_ft), 2)
                rows.append(
                    make_row('SUPPORTS & ARREST', 'sec-supports', 'HEAVY DIAGONAL BRACING', 'wood', diag_ft, rule.br_frame_w_in, rule.br_frame_h_in, 4)
                )

    # Calculate totals for Nails & Consumables
    total_cft = sum((r['l'] * r['w'] * r['h'] / 144.0) * r['nos'] for r in rows if r['mat'] == 'wood')
    total_sqft = sum((r['l'] * r['w']) * r['nos'] for r in rows if r['mat'] == 'plywood')

    est_nail_kg = round(max(0.5, (total_cft * rule.br_nail_kg_per_cft) + (total_sqft / 100.0 * rule.br_nail_kg_per_100sqft)), 2)

    # Surface area in sq.m for VCI / Polythene wrap
    surface_sqm = 2.0 * (l_m * w_m + l_m * h_m + w_m * h_m)
    vci_sqm = round(surface_sqm * (1.0 + rule.br_vci_overlap_pct / 100.0), 2)

    # Strapping length in meters
    strap_count = max(2, math.ceil(l_ft / max(rule.br_strapping_pitch_ft, 1.0)))
    strapping_mtr = round(2.0 * (w_m + h_m) * strap_count, 2)

    # Pick default Nail / Consumable part codes if present in PkpartcodeInfo
    nail_pc = PkpartcodeInfo.objects.filter(pc_code__istartswith='N').first()
    nail_code, nail_rate = _lookup_part_rate(nail_pc.pc_code if nail_pc else 'N300', 110.0)

    nails = [
        {
            'part_code': nail_code,
            'name': str(nail_pc.pc_stock_description) if (nail_pc and nail_pc.pc_stock_description) else 'Wire Nails (Auto)',
            'qty': est_nail_kg,
            'rate': round(nail_rate, 2),
        }
    ]

    consumables = [
        {
            'part_code': 'VCI-WRAP',
            'name': f'VCI / Polythene Sheet ({vci_sqm} sqm)',
            'qty': vci_sqm,
            'rate': 0.0,
        },
        {
            'part_code': 'STRAP-PET',
            'name': f'PET / Steel Strapping ({strap_count} straps, {strapping_mtr} mtr)',
            'qty': strapping_mtr,
            'rate': 0.0,
        },
    ]

    return JsonResponse({
        'status': 'success',
        'rule': {
            'id': rule.id,
            'name': rule.br_name,
            'size_m': f"{round(l_m, 2)} x {round(w_m, 2)} x {round(h_m, 2)} m",
            'weight_kg': weight_kg,
            'runner_spec': f"{rule.br_base_runner_w_in}x{rule.br_base_runner_h_in}\" x {runner_nos} nos",
            'ply_mm': rule.br_wall_ply_mm,
            'heavy_bracing': rule.br_heavy_bracing,
        },
        'rows': rows,
        'nails': nails,
        'consumables': consumables,
        'summary': {
            'total_cft': round(total_cft, 3),
            'total_sqft': round(total_sqft, 2),
            'est_nail_kg': est_nail_kg,
            'vci_sqm': vci_sqm,
            'strapping_mtr': strapping_mtr,
        },
    })
