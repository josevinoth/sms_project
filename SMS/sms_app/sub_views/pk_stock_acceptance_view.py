from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import PkacceptanceForm
from ..models import PkstockpurchasesInfo,PkcostingInfo,PkquotationsummaryInfo,StockMaintenance
from ..views import get_tracker_flags
from django.contrib import messages
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id

@login_required(login_url='login_page')
def pk_acceptance_add(request,retrival_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    na_assessment_num_id = request.session.get('na_assessment_id')
    if request.method == "GET":
        if retrival_id == 0:
            form = PkacceptanceForm()
        else:
            retrival=PkcostingInfo.objects.get(pk=retrival_id)
            form = PkacceptanceForm(instance=retrival)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'na_assessment_num_id': na_assessment_num_id,
                'na_customer_name_id': request.session.get('na_customer_name_id'),
                'na_customer_new_name_id': request.session.get('na_customer_new_name_id'),
                'ses_customer_po_id': request.session.get('ses_customer_po_id'),
                'current_step': 'acceptance',
                'tracker_flags': get_tracker_flags(na_assessment_num_id),
                }
        return render(request, "asset_mgt_app/pk_acceptance_add.html", context)
    else:
        if retrival_id == 0:
            form = PkacceptanceForm(request.POST)
            if form.is_valid():
                form.save()
                print("retrival Form is Valid")
                last_id = (PkcostingInfo.objects.latest('id')).id
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/pk_retrival_update/'+str(last_id))
            else:
                print("retrival Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            retrival = PkcostingInfo.objects.get(pk=retrival_id)
            form = PkacceptanceForm(request.POST,instance=retrival)
            if form.is_valid():
                retrival = form.save()
                
                # If accepted (status 2 or 4), log as retrieval in StockMaintenance if not already logged
                if retrival.ct_stock_status.id in [2, 4] and retrival.ct_stock_purchase_number:
                    purchase_ref = retrival.ct_stock_purchase_number.sm_stock_purchase_number or retrival.ct_stock_purchase_number.sm_invoice_no or f"SM-{retrival.ct_stock_purchase_number.id}"
                    ref_no = purchase_ref
                    if not StockMaintenance.objects.filter(sm_stock_type_id=2, sm_invoice_no=ref_no, sm_description__endswith=f"(Costing ID: {retrival.id})").exists():
                        try:
                            # Use ct_na_quantity which is the actual retrieved stock count
                            actual_qty = float(retrival.ct_na_quantity or retrival.ct_quantity or 0)
                            StockMaintenance.objects.create(
                                sm_stock_type_id=2, # Retrieval
                                sm_invoice_date=datetime.now().date(),
                                sm_invoice_no=ref_no,
                                sm_description=f"Retrieved via Acceptance for Assessment {retrival.ct_assessment_num.na_assessment_num if retrival.ct_assessment_num else 'N/A'} (Costing ID: {retrival.id})",
                                sm_partcode=retrival.ct_stock_purchase_number.sm_partcode,
                                sm_count=actual_qty,
                                sm_uom=retrival.ct_stock_purchase_number.sm_uom,
                                sm_updated_by_id=user_id
                            )
                        except Exception as e:
                            print(f"Error logging acceptance: {e}")

                #  AUTOMATIC RETURN LOGIC: If received (status 4) and has excess, create return ledger entry
                if retrival.ct_stock_status.id == 4:
                    if retrival.ct_exe_quantity_req and retrival.ct_exe_quantity_req > 0:
                        # Check if already returned to avoid duplicates
                        if not StockMaintenance.objects.filter(sm_stock_type_id=3, sm_description__contains=f"Costing ID: {retrival.id}").exists():
                            try:
                                sm_return = StockMaintenance.objects.create(
                                    sm_stock_type_id=3,  # Return
                                    sm_partcode=retrival.ct_part_code,
                                    sm_thickness=retrival.ct_exe_height_req or 0,
                                    sm_width=retrival.ct_exe_width_req or 0,
                                    sm_length=retrival.ct_exe_length_req or 0,
                                    sm_invoice_date=datetime.now().date(),
                                    sm_invoice_no=str(retrival.ct_assessment_num.na_assessment_num) if retrival.ct_assessment_num else "",
                                    sm_description=f"Automatic Excess Return from Assessment {retrival.ct_assessment_num.na_assessment_num if retrival.ct_assessment_num else 'N/A'} (Costing ID: {retrival.id})",
                                    sm_count=retrival.ct_exe_quantity_req or 0,
                                    sm_total_cft=retrival.ct_exe_sqrt_req or 0,
                                    sm_per_unit_cost=retrival.ct_rate or 0,
                                    sm_updated_by_id=user_id
                                )
                                # Generate Stock Maintenance number (Branch specific)
                                fy = get_financial_year()
                                branch_id = get_session_branch_id(request)
                                branch_code = get_branch_code(branch_id)
                                prefix = f"{fy}_{branch_code}_GRN_PK_"
                                sm_return.sm_stock_purchase_number = generate_next_number(StockMaintenance, 'sm_stock_purchase_number', prefix, 6)
                                sm_return.save(update_fields=['sm_stock_purchase_number'])

                                # Update excess status to 'Returned' (ID 5 usually)
                                if retrival.ct_excess_status and retrival.ct_excess_status.id == 3:
                                    from ..sub_models.excess_mod import ExcessStock
                                    try:
                                        retrival.ct_excess_status = ExcessStock.objects.get(id=5)
                                        retrival.save(update_fields=['ct_excess_status'])
                                    except ExcessStock.DoesNotExist:
                                        pass
                            except Exception as e:
                                print(f"Error automically logging return: {e}")

                messages.success(request, 'Stock Successfully Updated')
            else:
                print("retrival Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            # return redirect(request.META['HTTP_REFERER'])
        return redirect('/SMS/pk_acceptance_list')

# List retrival
@login_required(login_url='login_page')
def pk_acceptance_list(request):
    first_name = request.session.get('first_name')
    context = {
                'pk_retrival_list' : PkcostingInfo.objects.filter(ct_cost_type=8,ct_stock_status=2).order_by('-id'),
                'first_name': first_name,
                'current_step': 'acceptance',
               }
    return render(request,"asset_mgt_app/pk_acceptance_list.html",context)

#Delete retrival
@login_required(login_url='login_page')
def pk_acceptance_delete(request,retrival_id):
    retrival = PkcostingInfo.objects.get(pk=retrival_id)
    # Clean up both Retrieval (Type 2) and Return (Type 3) records linked to this costing ID
    StockMaintenance.objects.filter(sm_stock_type_id__in=[2, 3], sm_description__contains=f"(Costing ID: {retrival_id})").delete()
    retrival.delete()
    # return redirect('/SMS/pK_retrival_cancel')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def pK_acceptance_cancel(request):
    assessment_num_val = request.session.get('na_assessment_id')
    retrival_summary_id=PkquotationsummaryInfo.objects.get(qs_assessment_num=assessment_num_val).id
    return redirect('/SMS/pk_retrivalsummary_update/' + str(retrival_summary_id))