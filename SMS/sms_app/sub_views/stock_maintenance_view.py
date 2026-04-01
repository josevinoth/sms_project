from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .general_utils import get_financial_year, generate_next_number
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from ..sub_models.stock_maintenance_mod import StockMaintenance
from ..sub_models.part_code_mod import PkpartcodeInfo
from ..sub_forms.stock_maintenance_form import StockMaintenanceForm
from ..sub_models.my_user_mod import MyUser
from ..models import PkstockvebdorInfo


def get_stock_totals():
    from django.db.models import Sum, Q

    # Stock Types: 1=Purchase, 2=Retrival, 3=Return
    # Overall (Added) = Purchase (1) + Return (3)
    # Retrieved = Retrival (2)
    # Current (In-Hand) = (Purchase + Return) - Retrival
    
    overall = StockMaintenance.objects.filter(sm_stock_type_id__in=[1, 3]).aggregate(
        count=Sum('sm_count'),
        cft=Sum('sm_total_cft'),
        cost=Sum('sm_total_price')
    )
    
    retrieved = StockMaintenance.objects.filter(sm_stock_type_id=2).aggregate(
        count=Sum('sm_count'),
        cft=Sum('sm_total_cft'),
        cost=Sum('sm_total_price')
    )

    return {
        'overall_count': overall['count'] or 0,
        'overall_cft': overall['cft'] or 0,
        'overall_cost': overall['cost'] or 0,
        'retrieved_count': retrieved['count'] or 0,
        'retrieved_cft': retrieved['cft'] or 0,
        'retrieved_cost': retrieved['cost'] or 0,
        'current_count': (overall['count'] or 0) - (retrieved['count'] or 0),
        'current_cft': (overall['cft'] or 0) - (retrieved['cft'] or 0),
        'current_cost': (overall['cost'] or 0) - (retrieved['cost'] or 0),
    }


def get_part_totals(part_id):
    from django.db.models import Sum

    # Overall (Added) = Purchase (1) + Return (3)
    overall = StockMaintenance.objects.filter(sm_partcode_id=part_id, sm_stock_type_id__in=[1, 3]).aggregate(
        count=Sum('sm_count'),
        cft=Sum('sm_total_cft'),
        cost=Sum('sm_total_price')
    )
    
    # Retrieved = Retrival (2)
    retrieved = StockMaintenance.objects.filter(sm_partcode_id=part_id, sm_stock_type_id=2).aggregate(
        count=Sum('sm_count'),
        cft=Sum('sm_total_cft'),
        cost=Sum('sm_total_price')
    )

    return {
        'overall_count': overall['count'] or 0,
        'overall_cft': float(overall['cft'] or 0),
        'overall_cost': float(overall['cost'] or 0),
        'retrieved_count': retrieved['count'] or 0,
        'retrieved_cft': float(retrieved['cft'] or 0),
        'retrieved_cost': float(retrieved['cost'] or 0),
        'current_count': (overall['count'] or 0) - (retrieved['count'] or 0),
        'current_cft': float((overall['cft'] or 0) - (retrieved['cft'] or 0)),
        'current_cost': float((overall['cost'] or 0) - (retrieved['cost'] or 0)),
    }


@login_required
def stock_maintenance_list(request):
    partcode_id = request.GET.get('partcode')
    select_all = request.GET.get('select_all')

    items = StockMaintenance.objects.select_related('sm_stock_type', 'sm_partcode', 'sm_uom', 'sm_updated_by').order_by('-sm_created_at')

    if partcode_id:
        items = items.filter(sm_partcode_id=partcode_id)
        totals = get_part_totals(partcode_id)
    else:
        totals = get_stock_totals()

    if select_all == 'true':
        items = items[:1000]
    else:
        items = items[:50]

    partcodes = PkpartcodeInfo.objects.all().order_by('pc_code')

    context = {
        'items': items,
        'partcodes': partcodes,
        'selected_partcode': partcode_id,
        'totals': totals,
    }
    return render(request, 'asset_mgt_app/stock_maintenance_list.html', context)


@login_required
def stock_maintenance_add(request):
    # Clear sticky data if explicitly requested (e.g., from List page)
    if request.GET.get('new') == '1':
        if 'sticky_stock_data' in request.session:
            del request.session['sticky_stock_data']

    if request.method == 'POST':
        form = StockMaintenanceForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)

            # 🔥 FORCE UOM FROM POST
            uom_id = request.POST.get("sm_uom")
            if uom_id:
                obj.sm_uom_id = uom_id

            if hasattr(request.user, 'myuser'):
                obj.sm_updated_by = MyUser.objects.get(pk=request.user.pk)
            elif isinstance(request.user, MyUser):
                obj.sm_updated_by = request.user
            else:
                obj.sm_updated_by = MyUser.objects.get(pk=request.user.pk)

            obj.save()

            # Generate and update sm_stock_purchase_number based on financial year
            fy = get_financial_year()
            prefix = f"{fy}_GRN_PK_"
            obj.sm_stock_purchase_number = generate_next_number(StockMaintenance, 'sm_stock_purchase_number', prefix, 6)
            obj.save(update_fields=['sm_stock_purchase_number'])

            if obj.sm_invoice_no:
                vendor_matches = PkstockvebdorInfo.objects.filter(spv_vendor_bill=obj.sm_invoice_no)
                if vendor_matches.exists():
                    obj.sm_vendor = vendor_matches.first()
                    obj.save(update_fields=['sm_vendor'])

            # Store sticky data for next entry
            request.session['sticky_stock_data'] = {
                'sm_stock_type': str(obj.sm_stock_type.id) if obj.sm_stock_type else '',
                'sm_invoice_date': str(obj.sm_invoice_date) if obj.sm_invoice_date else '',
                'sm_invoice_no': obj.sm_invoice_no,
                'sm_partcode': str(obj.sm_partcode.id) if obj.sm_partcode else '',
                'sm_per_unit_cost': str(obj.sm_per_unit_cost),
                'sm_count': obj.sm_count,
            }
            messages.success(request, f"Stock item '{obj.sm_stock_purchase_number}' saved successfully!")
            return redirect('stock_maintenance_list')
    else:
        initial_data = request.session.get('sticky_stock_data', {})
        form = StockMaintenanceForm(initial=initial_data)

    items = StockMaintenance.objects.select_related('sm_stock_type', 'sm_partcode', 'sm_uom', 'sm_updated_by').order_by('-sm_created_at')[:1000]

    # If sticky part exists, show its totals initially to avoid jump
    sticky_part_id = request.session.get('sticky_stock_data', {}).get('sm_partcode')
    if sticky_part_id:
        totals = get_part_totals(sticky_part_id)
    else:
        totals = get_stock_totals()

    return render(request, 'asset_mgt_app/stock_maintenance_add.html', {
        'form': form,
        'items': items,
        'totals': totals
    })


@login_required
def stock_maintenance_add_for_vendor(request):
    vendor_id = request.session.get('ses_stock_vendor_id')
    if not vendor_id:
        messages.error(request, "No Vendor Bill selected.")
        return redirect('pk_stock_vendor_list')
        
    vendor_info = get_object_or_404(PkstockvebdorInfo, pk=vendor_id)

    # Clear sticky data if explicitly requested
    if request.GET.get('new') == '1':
        if 'sticky_stock_data' in request.session:
            del request.session['sticky_stock_data']

    if request.method == 'POST':
        form = StockMaintenanceForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)

            # FORCE UOM FROM POST
            uom_id = request.POST.get("sm_uom")
            if uom_id:
                obj.sm_uom_id = uom_id

            if hasattr(request.user, 'myuser'):
                obj.sm_updated_by = MyUser.objects.get(pk=request.user.pk)
            elif isinstance(request.user, MyUser):
                obj.sm_updated_by = request.user
            else:
                obj.sm_updated_by = MyUser.objects.get(pk=request.user.pk)
                
            # Set Vendor relation
            obj.sm_vendor = vendor_info

            obj.save()

            # Generate and update sm_stock_purchase_number based on financial year
            fy = get_financial_year()
            prefix = f"{fy}_GRN_PK_"
            obj.sm_stock_purchase_number = generate_next_number(StockMaintenance, 'sm_stock_purchase_number', prefix, 6)
            obj.save(update_fields=['sm_stock_purchase_number'])

            # Store sticky data for next entry
            request.session['sticky_stock_data'] = {
                'sm_stock_type': str(obj.sm_stock_type.id) if obj.sm_stock_type else '',
                'sm_invoice_date': str(obj.sm_invoice_date) if obj.sm_invoice_date else '',
                'sm_invoice_no': obj.sm_invoice_no,
                'sm_partcode': str(obj.sm_partcode.id) if obj.sm_partcode else '',
                'sm_per_unit_cost': str(obj.sm_per_unit_cost),
                'sm_count': obj.sm_count,
            }
            messages.success(request, f"Stock item '{obj.sm_stock_purchase_number}' saved successfully under Vendor Bill {vendor_info.spv_vendor_bill}!")
            return redirect('/SMS/pk_stock_vendor_update/' + str(vendor_id))
    else:
        initial_data = request.session.get('sticky_stock_data', {})
        
        # If the sticky data belongs to a different invoice, discard the sticky data!
        if initial_data.get('sm_invoice_no') and initial_data['sm_invoice_no'] != vendor_info.spv_vendor_bill:
            initial_data = {}
        else:
            initial_data = initial_data.copy()
        
        # Always enforce the current vendor's bill and date in the vendor-specific flow
        initial_data['sm_invoice_no'] = vendor_info.spv_vendor_bill
        if vendor_info.spv_vendor_bill_date:
            initial_data['sm_invoice_date'] = vendor_info.spv_vendor_bill_date
            
        form = StockMaintenanceForm(initial=initial_data)

    items = StockMaintenance.objects.select_related('sm_stock_type', 'sm_partcode', 'sm_uom', 'sm_updated_by').filter(sm_vendor=vendor_info).order_by('-sm_created_at')[:1000]

    # If sticky part exists, show its totals initially to avoid jump
    sticky_part_id = request.session.get('sticky_stock_data', {}).get('sm_partcode')
    if sticky_part_id:
        totals = get_part_totals(sticky_part_id)
    else:
        totals = get_stock_totals()

    return render(request, 'asset_mgt_app/stock_maintenance_add.html', {
        'form': form,
        'items': items,
        'totals': totals,
        'is_vendor_flow': True,
        'vendor_id': vendor_id
    })


@login_required
def stock_maintenance_edit(request, pk):
    item = get_object_or_404(StockMaintenance, pk=pk)

    if request.method == 'POST':
        form = StockMaintenanceForm(request.POST, instance=item)
        if form.is_valid():
            obj = form.save(commit=False)

            # 🔥 FORCE UOM AGAIN
            uom_id = request.POST.get("sm_uom")
            if uom_id:
                obj.sm_uom_id = uom_id

            if hasattr(request.user, 'myuser'):
                obj.sm_updated_by = MyUser.objects.get(pk=request.user.pk)
            elif isinstance(request.user, MyUser):
                obj.sm_updated_by = request.user
            else:
                obj.sm_updated_by = MyUser.objects.get(pk=request.user.pk)

            obj.save()
            return redirect('stock_maintenance_list')
    else:
        form = StockMaintenanceForm(instance=item)

    items = StockMaintenance.objects.all().order_by('-sm_created_at')

    # If editing, show part-specific totals initially to avoid jump
    if item.sm_partcode:
        totals = get_part_totals(item.sm_partcode.id)
    else:
        totals = get_stock_totals()

    return render(request, 'asset_mgt_app/stock_maintenance_add.html', {
        'form': form,
        'items': items,
        'totals': totals
    })


@login_required
def get_part_details(request):
    part_id = request.GET.get('part_id')

    data = {}
    if part_id:
        try:
            try:
                part = PkpartcodeInfo.objects.get(pk=part_id)
            except:
                part = PkpartcodeInfo.objects.get(pc_code=part_id)

            desc = str(part.pc_stock_description) if part.pc_stock_description else "NO DESC"

            part_totals = get_part_totals(part.id)

            data = {
                'partCodeText': part.pc_code,
                'description': desc,
                'thickness': part.pc_height or 0,
                'width': part.pc_width or 0,
                'length': part.pc_length or 0,
                'uom_id': part.pc_uom.id if part.pc_uom else "",
                'uom_name': part.pc_uom.unit_of_measure if part.pc_uom else "",
                'part_totals': part_totals
            }

        except Exception as e:
            data = {'error': str(e)}
    else:
        totals = get_stock_totals()
        data = {
            'part_totals': {
                'overall_count': totals['overall_count'],
                'overall_cft': float(totals['overall_cft']),
                'overall_cost': float(totals['overall_cost']),
                'retrieved_count': totals['retrieved_count'],
                'retrieved_cft': float(totals['retrieved_cft']),
                'retrieved_cost': float(totals['retrieved_cost']),
                'current_count': totals['current_count'],
                'current_cft': float(totals['current_cft']),
                'current_cost': float(totals['current_cost']),
            }
        }

    return JsonResponse(data)


@login_required
def stock_maintenance_delete(request, pk):
    item = get_object_or_404(StockMaintenance, pk=pk)
    messages.success(request, f"Stock item '{item.sm_stock_purchase_number}' deleted successfully.")
    item.delete()
    return redirect('stock_maintenance_list')

