from django.contrib.auth.decorators import login_required
from ..forms import IninspectreportForm
from ..models import User_extInfo,Ininspectreport
from django.shortcuts import render, redirect
import qrcode
from io import BytesIO
import qrcode.image.svg

@login_required(login_url='login_page')
def ininspectreport_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    context = {
        'ininspectreport_list': Ininspectreport.objects.all(),
        'first_name': first_name,
        'role': role,
    }
    return render(request, "asset_mgt_app/ininspectionreport_list.html", context)

@login_required(login_url='login_page')
def ininspectreport_add(request, ininspectreport_id=0):
    context = {}
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    if request.method == "GET":
        if ininspectreport_id == 0:
            form = IninspectreportForm()
        else:
            factory = qrcode.image.svg.SvgImage
            img = qrcode.make(request.POST.get("qr_text", ""), image_factory=factory, box_size=10)
            stream = BytesIO()
            img.save(stream)
            context["svg"] = stream.getvalue().decode()
            # print(context)
            ininspectreport = Ininspectreport.objects.get(pk=ininspectreport_id)
            form = IninspectreportForm(instance=ininspectreport)
        context={
            'form': form,
            'role': role,
            'first_name': first_name,
        }
        return render(request, "asset_mgt_app/ininspectionreport_add.html", context)
    else:
        if ininspectreport_id == 0:
            form = IninspectreportForm(request.POST)
        else:
            ininspectreport = Ininspectreport.objects.get(pk=ininspectreport_id)
            form = IninspectreportForm(request.POST, instance=ininspectreport)
        if form.is_valid():
            form.save()
        return redirect('/SMS/ininspectreport_list')

# Delete ininspectreport
@login_required(login_url='login_page')
def ininspectreport_delete(request, ininspectreport_id):
    ininspectreport = Ininspectreport.objects.get(pk=ininspectreport_id)
    ininspectreport.delete()
    return redirect('/SMS/ininspectreport_list')