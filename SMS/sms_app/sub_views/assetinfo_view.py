from django.contrib.auth.decorators import login_required
from ..forms import AssetinfoaddForm
from ..models import AssetInfo
from django.shortcuts import render, redirect
import qrcode
from io import BytesIO
import qrcode.image.svg

@login_required(login_url='login_page')
def asset_list(request):
    first_name = request.session.get('first_name')
    context = {'asset_list': AssetInfo.objects.all(),'first_name': first_name}
    return render(request, "asset_mgt_app/asset_list.html", context)

@login_required(login_url='login_page')
def assetinfo_add(request, asset_id=0):
    context = {}
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if asset_id == 0:
            form = AssetinfoaddForm()
        else:
            factory = qrcode.image.svg.SvgImage
            img = qrcode.make(request.POST.get("qr_text", ""), image_factory=factory, box_size=10)
            stream = BytesIO()
            img.save(stream)
            context["svg"] = stream.getvalue().decode()
            # print(context)
            assetinfo = AssetInfo.objects.get(pk=asset_id)
            form = AssetinfoaddForm(instance=assetinfo)
        return render(request, "asset_mgt_app/asset_add.html", {'form': form,'context': context,'first_name': first_name,})
    else:
        if asset_id == 0:
            form = AssetinfoaddForm(request.POST)
        else:
            assetinfo = AssetInfo.objects.get(pk=asset_id)
            form = AssetinfoaddForm(request.POST, instance=assetinfo)
        if form.is_valid():
            form.save()
        return redirect('/SMS/asset_list')

# Delete Assets
@login_required(login_url='login_page')
def asset_delete(request, asset_id):
    assetinfo = AssetInfo.objects.get(pk=asset_id)
    assetinfo.delete()
    return redirect('/SMS/asset_list')