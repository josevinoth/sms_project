from django.contrib.auth.decorators import login_required
from ..forms import ConsignmentdetailaddForm
from ..models import ConsignmentdetailInfo,EnquirynoteInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def transport_nav(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    con_det_form = ConsignmentdetailaddForm()
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'con_det_form': con_det_form,

    }
    return render(request, "asset_mgt_app/transport_nav.html", context)