from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import PkacceptanceForm
from ..models import PkstockpurchasesInfo,PkcostingInfo,PkquotationsummaryInfo,StockMaintenance
from ..views import update_reduced_dimensions,get_tracker_flags
from django.contrib import messages

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
                    ref_no = f"RET-{retrival.ct_stock_purchase_number.sm_stock_purchase_number}-{retrival.id}"
                    if not StockMaintenance.objects.filter(sm_invoice_no=ref_no).exists():
                        try:
                            StockMaintenance.objects.create(
                                sm_stock_type_id=2, # Retrieval
                                sm_invoice_date=datetime.now().date(),
                                sm_invoice_no=ref_no,
                                sm_description=f"Retrieved via Acceptance for Assessment {retrival.ct_assessment_num.na_assessment_num if retrival.ct_assessment_num else 'N/A'}",
                                sm_partcode=retrival.ct_stock_purchase_number.sm_partcode,
                                sm_count=float(retrival.ct_quantity or 0),
                                sm_uom=retrival.ct_stock_purchase_number.sm_uom,
                                sm_updated_by_id=user_id
                            )
                        except Exception as e:
                            print(f"Error logging acceptance: {e}")

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
    retrival.delete()
    # return redirect('/SMS/pK_retrival_cancel')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def pK_acceptance_cancel(request):
    assessment_num_val = request.session.get('na_assessment_id')
    retrival_summary_id=PkquotationsummaryInfo.objects.get(qs_assessment_num=assessment_num_val).id
    return redirect('/SMS/pk_retrivalsummary_update/' + str(retrival_summary_id))