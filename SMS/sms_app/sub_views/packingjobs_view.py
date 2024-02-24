from django.contrib.auth.decorators import login_required
from ..forms import PackingjobsForm
from ..models import User_extInfo,Packingjobs
from django.shortcuts import render, redirect
import qrcode
from io import BytesIO
import qrcode.image.svg

@login_required(login_url='login_page')
def packingjobs_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    context = {
        'packingjobs_list': Packingjobs.objects.all(),
        'first_name': first_name,
        'role': role,
    }
    return render(request, "asset_mgt_app/packingjobs_list.html", context)

@login_required(login_url='login_page')
def packingjobs_add(request, packingjobs_id=0):
    context = {}
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    if request.method == "GET":
        if packingjobs_id == 0:
            form = PackingjobsForm()
        else:
            factory = qrcode.image.svg.SvgImage
            img = qrcode.make(request.POST.get("qr_text", ""), image_factory=factory, box_size=10)
            stream = BytesIO()
            img.save(stream)
            context["svg"] = stream.getvalue().decode()
            # print(context)
            packingjobs = Packingjobs.objects.get(pk=packingjobs_id)
            form = PackingjobsForm(instance=packingjobs)
        context={
            'form': form,
            'role': role,
            'first_name': first_name,
        }
        return render(request, "asset_mgt_app/packingjobs_add.html", context)
    else:
        if packingjobs_id == 0:
            form = PackingjobsForm(request.POST)
        else:
            packingjobs = Packingjobs.objects.get(pk=packingjobs_id)
            form = PackingjobsForm(request.POST, instance=packingjobs)
        if form.is_valid():
            form.save()
        return redirect('/SMS/packingjobs_list')

# Delete packingjobs
@login_required(login_url='login_page')
def packingjobs_delete(request, packingjobs_id):
    packingjobs = Packingjobs.objects.get(pk=packingjobs_id)
    packingjobs.delete()
    return redirect('/SMS/packingjobs_list')