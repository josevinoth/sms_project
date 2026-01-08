from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages

from ..sub_forms.trans_invoice_Form import TransInvoiceForm
from ..sub_models.trans_invoice_mod import TransInvoiceInfo
from ..sub_models.customer_mod import CustomerInfo
from ..sub_models.tripdetail_mod import TripdetailInfo
from ..sub_models.consignmentdetail_mod import ConsignmentdetailInfo
from ..sub_models.consignmentgoods_mod import ConsignmentgoodsInfo



# ==================================================
# ADD / EDIT TRANS INVOICE
# ==================================================
@login_required(login_url='login_page')
def trans_invoice_add(request):
    first_name = request.session.get('first_name')

    saved = False

    if request.method == "POST":
        form = TransInvoiceForm(request.POST)

        if form.is_valid():
            invoice = form.save(commit=False)

            # calculate total
            invoice.ti_total = (
                (invoice.ti_transportation_charges or 0) +
                (invoice.ti_toll_charges or 0) +
                (invoice.ti_parking_charges or 0) +
                (invoice.ti_loading_charges or 0) +
                (invoice.ti_unloading_charges or 0) +
                (invoice.ti_halting_charges or 0) +
                (invoice.ti_docket_charges or 0) +
                (invoice.ti_weighment_charges or 0) +
                (invoice.ti_handling_charges or 0) +
                (invoice.ti_cancellation_charges or 0)
            )

            # latest consignment
            invoice.ti_consignment = (
                ConsignmentdetailInfo.objects
                .filter(co_customer=invoice.ti_customer)
                .order_by('-id')
                .first()
            )

            # latest trip & goods
            if invoice.ti_consignment:
                invoice.ti_trip = (
                    TripdetailInfo.objects
                    .filter(tr_consignmentnumber=invoice.ti_consignment)
                    .order_by('-id')
                    .first()
                )

                invoice.ti_goods = (
                    ConsignmentgoodsInfo.objects
                    .filter(cg_consignmentnumber=invoice.ti_consignment)
                    .order_by('-id')
                    .first()
                )

            invoice.save()


            saved = True

        else:
            messages.error(request, "Please check mandatory fields!")

    else:
        form = TransInvoiceForm()

    invoice_list = TransInvoiceInfo.objects.all().order_by('-id')

    return render(
        request,
        "asset_mgt_app/trans_invoice_Add.html",
        {
            'form': form,
            'invoice_list': invoice_list,
            'first_name': first_name,
            'saved': saved,
        }
    )

# ==================================================
# LIST TRANS INVOICE
# ==================================================
@login_required(login_url='login_page')
def trans_invoice_list(request):
    first_name = request.session.get('first_name')

    return render(
        request,
        "asset_mgt_app/trans_invoice_list.html",
        {
            'trans_invoice_list': TransInvoiceInfo.objects.all().order_by('-id'),
            'first_name': first_name,
        }
    )


# ==================================================
# DELETE TRANS INVOICE
# ==================================================
@login_required(login_url='login_page')
def trans_invoice_delete(request, invoice_id):
    invoice = get_object_or_404(TransInvoiceInfo, pk=invoice_id)
    invoice.delete()
    messages.success(request, "Transportation Invoice Deleted Successfully!")
    return redirect('trans_invoice_list')


# ==================================================
# AJAX – FETCH CUSTOMER DETAILS
# ==================================================
@login_required(login_url='login_page')
def fetch_customer_details(request):
    customer_id = request.GET.get('customer_id')

    customer = CustomerInfo.objects.filter(id=customer_id).first()

    if not customer:
        return JsonResponse({
            'gstin': '',
            'customer_short_name': '',
            'state': '',
            'pincode': ''
        })

    return JsonResponse({
        'gstin': customer.cu_gst or '',
        'customer_short_name': customer.cu_nameshort or '',
        'state': getattr(customer, 'cu_state', ''),
        'pincode': getattr(customer, 'cu_pincode', ''),
    })



@login_required(login_url='login_page')
def trans_invoice_list_woh(request, customer_id):
    first_name = request.session.get('first_name')

    # Filter by selected customer
    trans_invoice_list = (
        TransInvoiceInfo.objects
        .filter(is_woh=True, ti_customer_id=customer_id)
        .order_by('-id')
    )

    invoice_list_master = (
        TransInvoiceInfo.objects
        .filter(is_woh=False, ti_customer_id=customer_id)
        .order_by('-id')
    )

    customer = get_object_or_404(CustomerInfo, id=customer_id)

    return render(
        request,
        "asset_mgt_app/trans_invoice_list_WOH.html",
        {
            "trans_invoice_list": trans_invoice_list,
            "invoice_list_master": invoice_list_master,
            "customer": customer,
            "first_name": first_name,
        }
    )

@login_required(login_url='login_page')
def trans_invoice_remove_woh(request):
    ids = request.GET.getlist('invoice_list[]')

    TransInvoiceInfo.objects.filter(
        id__in=ids
    ).update(is_woh=False)

    messages.success(request, "Selected Transport Invoices removed from the list")
    return JsonResponse({'status': 'success'})


@login_required(login_url='login_page')
def trans_invoice_add_woh(request):
    ids = request.POST.getlist('ids[]')

    TransInvoiceInfo.objects.filter(
        id__in=ids
    ).update(is_woh=True)

    messages.success(request, "Selected Transport Invoices added to the list")
    return JsonResponse({'status': 'success'})
