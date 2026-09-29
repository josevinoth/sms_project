from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from ..models import Ar_Info


@login_required(login_url='login_page')
def ar_receipt_list(request):
    ar_qs = Ar_Info.objects.filter(
        Q(ar_payment_received_date__isnull=False) | Q(ar_payment_received_amount__gt=0)
    ).select_related(
        'ar_company',
        'ar_product',
        'ar_branch',
        'ar_customer_name',
        'ar_customer_dept',
        'ar_sales_person',
        'ar_invoice_num',
    ).order_by('-ar_payment_received_date', '-id')

    first_name = request.session.get('first_name')

    rows = []
    for ar in ar_qs:
        rows.append({
            'company': ar.ar_company.bvm_business if ar.ar_company else '-',
            'product': ar.ar_product.bp_product if ar.ar_product else '-',
            'branch': ar.ar_branch.loc_name if ar.ar_branch else '-',
            'op_date': ar.ar_operation_date.strftime('%d/%m/%Y') if ar.ar_operation_date else '-',
            'inv_no': str(ar.ar_invoice_num) if ar.ar_invoice_num else '-',
            'inv_date': ar.ar_invoice_date.strftime('%d/%m/%Y') if ar.ar_invoice_date else '-',
            'customer': ar.ar_customer_name.cu_name if ar.ar_customer_name else '-',
            'dept': ar.ar_customer_dept.ct_customerdepartment if ar.ar_customer_dept else '-',
            'service_val': ar.ar_service_value or 0.0,
            'cgst': ar.ar_cgst or 0.0,
            'sgst': ar.ar_sgst or 0.0,
            'igst': ar.ar_igst or 0.0,
            'amount': ar.ar_amount or 0.0,
            'sub_date': ar.ar_submission_date.strftime('%d/%m/%Y') if ar.ar_submission_date else '-',
            'inv_sent_to': ar.ar_invoice_sent_to or '-',
            'payment_received_date': ar.ar_payment_received_date.strftime('%d/%m/%Y') if ar.ar_payment_received_date else '-',
            'payment_received_amount': ar.ar_payment_received_amount or 0.0,
            'tds': ar.ar_tds or 0.0,
            'rec_from_op_date': ar.ar_rec_from_operation_date or '-',
            'rec_from_inv_date': ar.ar_rec_from_invoice_date or '-',
            'rec_from_sub_date': ar.ar_rec_from_submission_date or '-',
            'id': ar.id,
            'sales': ar.ar_sales_person.get_full_name() if ar.ar_sales_person else '-',
        })

    metrics = {
        'total_count': len(rows),
        'total_amount': sum(r['amount'] for r in rows),
        'total_received': sum(r['payment_received_amount'] for r in rows),
        'total_tds': sum(r['tds'] for r in rows),
    }

    return render(request, 'asset_mgt_app/ar_receipt_list.html', {
        'rows': rows,
        'metrics': metrics,
        'first_name': first_name,
    })
