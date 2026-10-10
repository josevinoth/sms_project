from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from ..sub_models.tms_petty_cash_mod import TMSPettyCashInfo
from ..sub_models.wms_petty_cash_mod import WMSPettyCashInfo
from ..sub_models.pms_petty_cash_mod import PMSPettyCashInfo

def petty_cash_approval_list(request):
    user_id = request.user.id
    emp_branch_id = request.session.get('ses_emp_branch_id')
    
    tms_qs = TMSPettyCashInfo.objects.all()
    wms_qs = WMSPettyCashInfo.objects.all()
    pms_qs = PMSPettyCashInfo.objects.all()
    
    # Filter by user's branch if not a superuser and branch is available, 
    # and bypass filter for the designated approver IDs
    approver_ids = [27, 28, 74, 115]
    if emp_branch_id and not request.user.is_superuser and user_id not in approver_ids:
        tms_qs = tms_qs.filter(tpc_branch_id=emp_branch_id)
        wms_qs = wms_qs.filter(wpc_branch_id=emp_branch_id)
        pms_qs = pms_qs.filter(ppc_branch_id=emp_branch_id)
        
    tms_list = tms_qs.order_by('-id')
    wms_list = wms_qs.order_by('-id')
    pms_list = pms_qs.order_by('-id')
    
    context = {
        'tms_list': tms_list,
        'wms_list': wms_list,
        'pms_list': pms_list,
        'user_id': user_id
    }
    return render(request, 'asset_mgt_app/petty_cash_approval_list.html', context)

def approve_petty_cash(request, sys_type, pc_id, action):
    # sys_type: 'tms', 'wms', 'pms'
    # action: 'check', 'verify', 'approve'
    if sys_type == 'tms':
        obj = get_object_or_404(TMSPettyCashInfo, pk=pc_id)
        prefix = 'tpc'
    elif sys_type == 'wms':
        obj = get_object_or_404(WMSPettyCashInfo, pk=pc_id)
        prefix = 'wpc'
    else:
        obj = get_object_or_404(PMSPettyCashInfo, pk=pc_id)
        prefix = 'ppc'

    if action == 'check':
        setattr(obj, f'{prefix}_is_checked', True)
        setattr(obj, f'{prefix}_checked_by', request.user)
        setattr(obj, f'{prefix}_checked_at', timezone.now())
    elif action == 'verify':
        if not getattr(obj, f'{prefix}_is_checked'):
            messages.error(request, 'Cannot verify before it is checked.')
            return redirect('petty_cash_approval_list')
        setattr(obj, f'{prefix}_is_verified', True)
        setattr(obj, f'{prefix}_verified_by', request.user)
        setattr(obj, f'{prefix}_verified_at', timezone.now())
    elif action == 'approve':
        if not getattr(obj, f'{prefix}_is_verified'):
            messages.error(request, 'Cannot approve before it is verified.')
            return redirect('petty_cash_approval_list')
        setattr(obj, f'{prefix}_is_approved', True)
        setattr(obj, f'{prefix}_approved_by', request.user)
        setattr(obj, f'{prefix}_approved_at', timezone.now())
        
    obj.save()
    messages.success(request, f"Successfully {action}d voucher.")
    return redirect('petty_cash_approval_list')
