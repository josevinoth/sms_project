from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from ..forms import PkneedassessmentForm,NadimensionForm
from ..models import  PkquotationsummaryInfo,PkquotationInfo,POdimension,Natypeofreq,Unitofmeasure,Naconsumables,VehicletypeInfo,Pkstocktype,Pkwooddescription,Nadimensiontype,PkpurchaseorderInfo,PkcostingsummaryInfo,PkcostingInfo,commentsInfo,User_extInfo,PkneedassessmentInfo,Nadimension
from django.shortcuts import render, redirect, get_object_or_404
from random import randint
from django.contrib import messages
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id

def get_tracker_flags(na_id):
    """
    Return a dict of completed flags for each PMS stage.
    A stage is 'done' (green) if its status FK has id == 5 (Completed).
    """
    flags = {
        'assessment_done': False,
        'quotation_done': False,
        'po_done': False,
        'costing_done': False,
        'acceptance_done': False,
    }
    if not na_id:
        return flags
    try:
        na = PkneedassessmentInfo.objects.get(pk=na_id)
        flags['assessment_done'] = bool(na.na_status and na.na_status.id == 5)
    except PkneedassessmentInfo.DoesNotExist:
        pass

    qs = PkquotationsummaryInfo.objects.filter(qs_assessment_num=na_id).first()
    if qs:
        flags['quotation_done'] = bool(qs.qs_status and qs.qs_status.id == 5)

    po = PkpurchaseorderInfo.objects.filter(po_assessment_num=na_id).first()
    if po:
        flags['po_done'] = bool(po.po_status and po.po_status.id == 5)

    cs = PkcostingsummaryInfo.objects.filter(cs_assessment_num=na_id).first()
    if cs:
        flags['costing_done'] = bool(cs.cs_status and cs.cs_status.id == 5)

    # Acceptance: all stock items (cost_type=8) are received (status=4)
    stock_items = PkcostingInfo.objects.filter(ct_assessment_num=na_id, ct_cost_type=8)
    if stock_items.exists() and all(i.ct_stock_status_id == 4 for i in stock_items):
        flags['acceptance_done'] = True

    return flags


@login_required(login_url='login_page')
def needassessment_add(request,needassessment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role

    if request.method == "GET":
        if needassessment_id == 0:
            form = PkneedassessmentForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'role': role,
            }
        else:
            needassessment=PkneedassessmentInfo.objects.get(pk=needassessment_id)
            form = PkneedassessmentForm(instance=needassessment)
            needassessment_id=PkneedassessmentInfo.objects.get(pk=needassessment_id).id
            needassessment_num=PkneedassessmentInfo.objects.get(pk=needassessment_id).na_assessment_num
            request.session['na_assessment_id'] = needassessment_id
            request.session['na_assessment_num'] = needassessment_num
            na_dimension_list=Nadimension.objects.filter(nad_assess_num=needassessment_id)
            comments_list= commentsInfo.objects.filter(comments_ref=needassessment_num)
            
            # Fetch linked quotations for the hub
            linked_quotations = PkquotationsummaryInfo.objects.filter(qs_assessment_num=needassessment_id)
            
            context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'role': role,
                'na_dimension_list': na_dimension_list,
                'comments_list': comments_list,
                'linked_quotations': linked_quotations,
                'current_step': 'assessment',
                'tracker_flags': get_tracker_flags(needassessment_id),
                }
        return render(request, "asset_mgt_app/pk_needassessment_add.html", context)
    else:
        if needassessment_id == 0:
            form = PkneedassessmentForm(request.POST,request.FILES)
            if form.is_valid():
                # Generate Random Assessment number
                # Save the form but don't commit immediately
                instance = form.save(commit=False)
                instance.save()  # Now the ID is generated
                form.save_m2m()  # CRITICAL: Save Many-to-Many fields when using commit=False

                # Generate assessment number based on the financial year and next sequence (Branch specific)
                fy = get_financial_year()
                branch_id = get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                prefix = f"{fy}_{branch_code}_AS_"
                assessment_num_next = generate_next_number(PkneedassessmentInfo, 'na_assessment_num', prefix, 6)

                # Update the field and save only that field
                instance.na_assessment_num = assessment_num_next
                instance.save(update_fields=['na_assessment_num'])

                messages.success(request, 'Record Updated Successfully with Assessment Number: ' + assessment_num_next)
                return redirect(f'/SMS/needassessment_update/{instance.id}')
            else:
                print("needassessment Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')

                for field, errors in form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"Error in {field}: {error}")

                return redirect(request.META['HTTP_REFERER'])
        else:
            needassessment = PkneedassessmentInfo.objects.get(pk=needassessment_id)
            form = PkneedassessmentForm(request.POST,request.FILES,instance=needassessment)
            if form.is_valid():
                form.save()
                print("needassessment Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("needassessment Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List needassessment
@login_required(login_url='login_page')
def needassessment_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    context = {
            'needassessment_list' : PkneedassessmentInfo.objects.all(),
            'first_name': first_name,
            'role': role,
        }
    return render(request,"asset_mgt_app/pk_needassessment_list.html",context)

#Delete needassessment
@login_required(login_url='login_page')
def needassessment_delete(request,needassessment_id):
    needassessment = PkneedassessmentInfo.objects.get(pk=needassessment_id)
    assessment_num = needassessment.na_assessment_num

    # Deleting PkcostingInfo objects
    Pkcosting_delete(assessment_num)

    # Deleting Pkcosting summary objects
    Pkcostingsummary_delete(assessment_num)

    # Deleting Pkpurchaseorders objects
    Pkpurchaseorder_delete(assessment_num)

    # Deleting Pkpurchaseorders dims objects
    Pkpurchaseorder_dim_delete(assessment_num)

    #Deleting Pkquotations objects
    Pkquotation_delete(assessment_num)

    # Deleting quotation summary objects
    Pkquotation_summary_delete(assessment_num)

    # Deleting Pkneedassessment dims objects
    Pkneedassessment_dim_delete(assessment_num)

    # Deleting need assessment objects
    needassessment.delete()

    return redirect('/SMS/needassessment_list')


def Pkcosting_delete(assessment_num, job_no=None):
    try:
        if job_no:
            # Safer: Only delete lines for this SPECIFIC Job
            costing_objects = PkcostingInfo.objects.filter(ct_job_no=job_no)
        else:
            # Legacy: Delete everything for this Assessment
            costing_objects = PkcostingInfo.objects.filter(ct_assessment_num=assessment_num)

        if costing_objects.exists():
            costing_objects.delete()
    except Exception as e:
        print(f"Error in Pkcosting_delete: {e}")


def Pkcostingsummary_delete(assessment_num, job_no=None):
    try:
        if job_no:
            summaries = PkcostingsummaryInfo.objects.filter(cs_job_no=job_no)
        else:
            summaries = PkcostingsummaryInfo.objects.filter(cs_assessment_num=assessment_num)
            
        if summaries.exists():
            summaries.delete()
    except Exception as e:
        print(f"Error in Pkcostingsummary_delete: {e}")


def Pkpurchaseorder_delete(assessment_num):
    # Deleting PkpurchaseorderInfo objects
    try:
        customer_po_objects = PkpurchaseorderInfo.objects.filter(po_assessment_num=assessment_num)
        if customer_po_objects.exists():
            customer_po_objects.delete()
        else:
            print("No matching PkpurchaseorderInfo found to delete.")
    except Exception as e:
        print(f"An error occurred while deleting PkpurchaseorderInfo: {e}")


def Pkpurchaseorder_dim_delete(assessment_num):
    # Deleting Pkpurchaseorder dimension objects
    try:
        customer_po_dim_objects = POdimension.objects.filter(pod_assess_num=assessment_num)
        if customer_po_dim_objects.exists():
            customer_po_dim_objects.delete()
        else:
            print("No matching Pkpurchaseorder dimensions found to delete.")
    except Exception as e:
        print(f"An error occurred while deleting Pkpurchaseorder dimensions: {e}")


def Pkquotation_delete(assessment_num):
    # Deleting PkquotationInfo objects
    try:
        quotation_objects = PkquotationInfo.objects.filter(pkqt_assessment_num=assessment_num)
        if quotation_objects.exists():
            quotation_objects.delete()
        else:
            print("No matching PkquotationInfo found to delete.")
    except Exception as e:
        print(f"An error occurred while deleting PkquotationInfo: {e}")


def Pkquotation_summary_delete(assessment_num):
    # Deleting PkquotationsummaryInfo objects
    try:
        quotationsummary_objects = PkquotationsummaryInfo.objects.filter(qs_assessment_num=assessment_num)
        if quotationsummary_objects.exists():
            quotationsummary_objects.delete()
        else:
            print("No matching PkquotationsummaryInfo found to delete.")
    except Exception as e:
        print(f"An error occurred while deleting PkquotationsummaryInfo: {e}")

def Pkneedassessment_dim_delete(assessment_num):
    try:
        # Fetch the queryset for the matching records
        na_dim_objects = Nadimension.objects.filter(nad_assess_num=assessment_num)

        # Check if any objects were found
        if na_dim_objects.exists():
            # Delete the objects
            na_dim_objects.delete()
        else:
            # Handle the case where no objects were found, if needed
            print("No matching costing info found to delete.")
    except Exception as e:
        # Handle any unexpected exceptions
        print(f"An error occurred: {e}")

@login_required(login_url='login_page')
def na_dimension_cancel(request,needassessment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    needassessment_id=request.session.get('na_assessment_id')
    return redirect('/SMS/needassessment_update/' + str(needassessment_id))
@login_required(login_url='login_page')
def na_dimension_add(request, na_dimension_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role_id = User_extInfo.objects.get(user=user_id).emp_role.id
    na_assessment_num_id = request.session.get('na_assessment_id')
    # Retrieve related status from PkneedassessmentInfo
    na_status = None
    if na_assessment_num_id:
        try:
            assessment_instance = PkneedassessmentInfo.objects.get(id=na_assessment_num_id)
            na_status = assessment_instance.na_status.id if assessment_instance.na_status else None
        except PkneedassessmentInfo.DoesNotExist:
            na_status = None

    if request.method == "GET":
        if na_dimension_id == 0:
            # Get session values and only prefill if it's the SAME assessment
            last_assessment_id = request.session.get('last_nad_assessment_id')
            
            if last_assessment_id and str(last_assessment_id) == str(na_assessment_num_id):
                wood_type_ids = request.session.get('last_nad_wood_type_list', [])
                wood_desc_ids = request.session.get('last_nad_wood_description_list', [])

                initial_data = {
                    'nad_type_of_req': Natypeofreq.objects.filter(id=request.session.get('last_nad_type_of_req')).first(),
                    'nad_quantity': request.session.get('last_nad_quantity'),
                    'nad_consumables': Naconsumables.objects.filter(id=request.session.get('last_nad_consumables')).first(),
                    'nad_vechicle_type': VehicletypeInfo.objects.filter(id=request.session.get('last_nad_vechicle_type')).first(),
                    'nad_uom': Unitofmeasure.objects.filter(id=request.session.get('last_nad_uom')).first(),
                    'nad_dimension_type': Nadimensiontype.objects.filter(id=request.session.get('last_nad_dimension_type')).first(),
                }

                form = NadimensionForm(initial=initial_data)

                # Prefill ManyToMany after form init
                if wood_type_ids:
                    form.fields['nad_wood_type'].initial = Pkstocktype.objects.filter(id__in=wood_type_ids)
                if wood_desc_ids:
                    form.fields['nad_wood_description'].initial = Pkwooddescription.objects.filter(id__in=wood_desc_ids)
            else:
                form = NadimensionForm()

        else:
            na_dimensioninfo = Nadimension.objects.get(pk=na_dimension_id)
            form = NadimensionForm(instance=na_dimensioninfo)

        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'role_id': role_id,
            'na_assessment_num_id': na_assessment_num_id,
            'na_status': na_status,  # Pass to template
        }

        return render(request, "asset_mgt_app/na_dimension_add.html", context)

    else:
        if na_dimension_id == 0:
            form = NadimensionForm(request.POST)
            if form.is_valid():
                instance = form.save()
                # Generate Item number based on financial year (Branch specific)
                fy = get_financial_year()
                branch_id = get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                prefix = f"{fy}_{branch_code}_ITM_"
                na_item_num_next = generate_next_number(Nadimension, 'nad_item', prefix, 6)
                Nadimension.objects.filter(id=instance.id).update(nad_item=na_item_num_next)

                # Store last submitted values in session
                request.session['last_nad_type_of_req'] = form.cleaned_data['nad_type_of_req'].id if form.cleaned_data.get('nad_type_of_req') else None
                request.session['last_nad_quantity'] = form.cleaned_data.get('nad_quantity')

                request.session['last_nad_wood_type_list'] = [obj.id for obj in form.cleaned_data.get('nad_wood_type')] if form.cleaned_data.get('nad_wood_type') else []
                request.session['last_nad_wood_description_list'] = [obj.id for obj in form.cleaned_data.get('nad_wood_description')] if form.cleaned_data.get('nad_wood_description') else []

                request.session['last_nad_consumables'] = form.cleaned_data['nad_consumables'].id if form.cleaned_data.get('nad_consumables') else None
                request.session['last_nad_vechicle_type'] = form.cleaned_data['nad_vechicle_type'].id if form.cleaned_data.get('nad_vechicle_type') else None
                request.session['last_nad_uom'] = form.cleaned_data['nad_uom'].id if form.cleaned_data.get('nad_uom') else None
                request.session['last_nad_dimension_type'] = form.cleaned_data['nad_dimension_type'].id if form.cleaned_data.get('nad_dimension_type') else None
                request.session['last_nad_assessment_id'] = na_assessment_num_id

                messages.success(request, "Record Saved Successfully")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
                messages.error(request, "Record Not Saved")
        else:
            na_dimensioninfo = Nadimension.objects.get(pk=na_dimension_id)
            form = NadimensionForm(request.POST, instance=na_dimensioninfo)
            if form.is_valid():
                form.save()
                messages.success(request, "Record Updated Successfully")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
                messages.error(request, "Update Failed")

            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def na_dimension_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    context = {
        'user_id': user_id,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/na_dimension_list.html", context)
@login_required(login_url='login_page')
def na_dimension_delete(request, na_dimension_id):
    na_dimensioninfo = Nadimension.objects.get(pk=na_dimension_id)
    na_dimensioninfo.delete()
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/sales_list')

@login_required(login_url='login_page')
def need_assessment_print_pdf(request, assessment_id):
    try:
        need_assessment = PkneedassessmentInfo.objects.get(pk=assessment_id)
        dimensions = Nadimension.objects.filter(nad_assess_num=need_assessment)

        today = datetime.now().strftime("%d-%b-%Y")

        context = {
            "need_assessment": need_assessment,
            "dimensions": dimensions,
            "today_date": today,
        }

        file_name = f"NeedAssessment_{need_assessment.na_assessment_num}.pdf"
        template_path = 'asset_mgt_app/need_assessment_print.html'  # customize

        template = get_template(template_path)
        html = template.render(context)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse(f"Error during PDF generation: <pre>{html}</pre>")
        return response

    except PkneedassessmentInfo.DoesNotExist:
        return HttpResponse("Assessment not found", status=404)
