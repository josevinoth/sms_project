from django.contrib.auth.decorators import login_required
from ..forms import OuinspectreportForm
from ..models import User_extInfo,Ouinspectreport
from django.shortcuts import render, redirect
import qrcode
from io import BytesIO
import qrcode.image.svg

@login_required(login_url='login_page')
def ouinspectreport_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    context = {
        'ouinspectreport_list': Ouinspectreport.objects.all(),
        'first_name': first_name,
        'role': role,
    }
    return render(request, "asset_mgt_app/ouinspectionreport_list.html", context)

@login_required(login_url='login_page')
def ouinspectreport_add(request, ouinspectreport_id=0):
    context = {}
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    if request.method == "GET":
        if ouinspectreport_id == 0:
            form = OuinspectreportForm()
        else:
            factory = qrcode.image.svg.SvgImage
            img = qrcode.make(request.POST.get("qr_text", ""), image_factory=factory, box_size=10)
            stream = BytesIO()
            img.save(stream)
            context["svg"] = stream.getvalue().decode()
            # print(context)
            ouinspectreport = Ouinspectreport.objects.get(pk=ouinspectreport_id)
            form = OuinspectreportForm(instance=ouinspectreport)
        context={
            'form': form,
            'role': role,
            'first_name': first_name,
        }
        return render(request, "asset_mgt_app/ouinspectionreport_list.html", context)
    else:
        if ouinspectreport_id == 0:
            form = OuinspectreportForm(request.POST)
        else:
            ouinspectreport = Ouinspectreport.objects.get(pk=ouinspectreport_id)
            form = OuinspectreportForm(request.POST, instance=ouinspectreport)
        if form.is_valid():
            form.save()
        return redirect('/SMS/ouinspectreport_list')

# Delete ouinspectreport
@login_required(login_url='login_page')
def ouinspectreport_delete(request, ouinspectreport_id):
    ouinspectreport = Ouinspectreport.objects.get(pk=ouinspectreport_id)
    ouinspectreport.delete()
    return redirect('/SMS/ouinspectreport_list')