from ..models import AssetInfo
from django.shortcuts import render
import qrcode
from io import BytesIO

def qr_code_asset(request,asset_qr_id):
    first_name = request.session.get('first_name')
    qr_id = {
        AssetInfo.objects.get(pk=asset_qr_id).asset_number,
        AssetInfo.objects.get(pk=asset_qr_id).asset_assignedto,
        AssetInfo.objects.get(pk=asset_qr_id).asset_location
    }
    factory = qrcode.image.svg.SvgImage
    #img = qrcode.make(request.POST.get("qr_text", ""), image_factory=factory, box_size=10)
    img = qrcode.make(qr_id, image_factory=factory, box_size=10)
    stream = BytesIO()
    img.save(stream)
    context= {'svg':stream.getvalue().decode(),
              'Asset_Number':AssetInfo.objects.get(pk=asset_qr_id).asset_number,
              'Asset_Assigned_To': AssetInfo.objects.get(pk=asset_qr_id).asset_assignedto,
              'Asset_Location':AssetInfo.objects.get(pk=asset_qr_id).asset_location,
              'first_name': first_name
              }
    return render(request, "asset_mgt_app/qr_code.html", context=context)
