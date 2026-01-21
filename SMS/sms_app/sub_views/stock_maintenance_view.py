from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from ..sub_models.stock_maintenance_mod import StockMaintenance
from ..sub_models.part_code_mod import PkpartcodeInfo
from ..sub_forms.stock_maintenance_form import StockMaintenanceForm

def get_stock_totals():
    totals = StockMaintenance.objects.aggregate(
        total_count=Sum('sm_count'),
        total_cft=Sum('sm_total_cft'),
        total_cost=Sum('sm_total_price'),
    )
    return {
        'total_count': totals['total_count'] or 0,
        'total_cft': totals['total_cft'] or 0,
        'total_cost': totals['total_cost'] or 0,
    }

@login_required
def stock_maintenance_list(request):
    items = StockMaintenance.objects.all().order_by('-sm_created_at')
    return render(request, 'asset_mgt_app/stock_maintenance_list.html', {'items': items})

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

            obj.save()

            # Store sticky data for next entry
            request.session['sticky_stock_data'] = {
                'sm_stock_type': str(obj.sm_stock_type.id) if obj.sm_stock_type else '',
                'sm_invoice_date': str(obj.sm_invoice_date) if obj.sm_invoice_date else '',
                'sm_invoice_no': obj.sm_invoice_no,
                'sm_partcode': str(obj.sm_partcode.id) if obj.sm_partcode else '',
                'sm_per_unit_cost': str(obj.sm_per_unit_cost),
                'sm_count': obj.sm_count,
            }
            return redirect('stock_maintenance_add')
    else:
        initial_data = request.session.get('sticky_stock_data', {})
        form = StockMaintenanceForm(initial=initial_data)

    items = StockMaintenance.objects.all().order_by('-sm_created_at')
    totals = get_stock_totals()
    return render(request, 'asset_mgt_app/stock_maintenance_add.html', {
        'form': form, 
        'items': items,
        'totals': totals
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

            obj.save()
            return redirect('stock_maintenance_list')
    else:
        form = StockMaintenanceForm(instance=item)

    items = StockMaintenance.objects.all().order_by('-sm_created_at')
    totals = get_stock_totals()
    return render(request, 'asset_mgt_app/stock_maintenance_add.html', {
        'form': form, 
        'items': items,
        'totals': totals
    })


@login_required
def get_part_details(request):
    part_id = request.GET.get('part_id')

    # helper to log works better than print for me
    def log_debug(msg):
        try:
            with open(r'c:\Users\Admin\PycharmProjects\sms_project_v1\SMS\sms_debug.log', 'a') as f:
                f.write(f"{msg}\n")
        except Exception as e:
            pass

    log_debug(f"DEBUG: get_part_details called with part_id={part_id}")
    data = {}
    if part_id:
        try:
            # Handle whether input is ID(int) or Code(str)
            # Try by Code first (string)
            try:
                part = PkpartcodeInfo.objects.get(pc_code=str(part_id))
            except (PkpartcodeInfo.DoesNotExist, ValueError):
                # Only if not found by code, try by PK (ID)
                part = PkpartcodeInfo.objects.get(pk=part_id)

            # Safe access to fields
            desc = str(part.pc_stock_description) if part.pc_stock_description else "NO DESC"
            thk = part.pc_height if part.pc_height is not None else 0.0
            wid = part.pc_width if part.pc_width is not None else 0.0
            ln = part.pc_length if part.pc_length is not None else 0.0

            # Safe access to UOM ID and Name
            uid = part.pc_uom.id if part.pc_uom else None
            uname = str(part.pc_uom.unit_of_measure) if part.pc_uom else ""

            # Aggregated totals for this part
            part_totals = StockMaintenance.objects.filter(sm_partcode=part).aggregate(
                total_count=Sum('sm_count'),
                total_cft=Sum('sm_total_cft'),
                total_cost=Sum('sm_total_price')
            )

            data = {
                'description': desc,
                'thickness': part.pc_height or 0,
                'width': part.pc_width or 0,
                'length': part.pc_length or 0,
                'uom_id': part.pc_uom.id if part.pc_uom else "",
                'uom_name': part.pc_uom.unit_of_measure if part.pc_uom else "",
                'part_totals': {
                    'total_count': part_totals['total_count'] or 0,
                    'total_cft': float(part_totals['total_cft'] or 0),
                    'total_cost': float(part_totals['total_cost'] or 0),
                }
            }
            log_debug(f"DEBUG: Returning data: {data}")
        except PkpartcodeInfo.DoesNotExist:
            log_debug(f"DEBUG: Part with id {part_id} not found")
            data = {'error': 'Part not found'}
        except ValueError:
             data = {'error': 'Invalid Part ID'}
        except Exception as e:
            log_debug(f"DEBUG: Exception: {e}")
            data = {'error': str(e)}

    return JsonResponse(data)

@login_required
def stock_maintenance_delete(request, pk):
    item = get_object_or_404(StockMaintenance, pk=pk)
    item.delete()
    return redirect('stock_maintenance_list')

