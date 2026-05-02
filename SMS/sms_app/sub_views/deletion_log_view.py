from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import DeletionLog

@login_required(login_url='login_page')
def deletion_log_list(request):
    logs = DeletionLog.objects.all().order_by('-dl_deleted_at')
    return render(request, 'asset_mgt_app/deletion_log_list.html', {'logs': logs})
