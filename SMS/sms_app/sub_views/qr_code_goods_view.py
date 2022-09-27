from ..models import Warehouse_goods_info
from django.shortcuts import render
import qrcode
from io import BytesIO

def qr_code_goods(request,goods_qr_id):
    first_name = request.session.get('first_name')
    qr_id_goods = {
        Warehouse_goods_info.objects.get(pk=goods_qr_id).wh_qr_rand_num,
    }
    print(qr_id_goods)
    factory_goods = qrcode.image.svg.SvgImage
    #img = qrcode.make(request.POST.get("qr_text", ""), image_factory=factory, box_size=10)
    img = qrcode.make(qr_id_goods, image_factory=factory_goods, box_size=10)
    stream = BytesIO()
    img.save(stream)
    img.save('../qrcode_test2.png')
    context= {'svg':stream.getvalue().decode(),
              'Invoice_Number': Warehouse_goods_info.objects.get(pk=goods_qr_id).wh_goods_invoice,
              'Stock_Number':Warehouse_goods_info.objects.get(pk=goods_qr_id).wh_qr_rand_num,
              'Package_Type': Warehouse_goods_info.objects.get(pk=goods_qr_id).wh_goods_package_type,
              'Area': Warehouse_goods_info.objects.get(pk=goods_qr_id).wh_goods_area,
              'Volume': Warehouse_goods_info.objects.get(pk=goods_qr_id).wh_goods_volume_weight,
              'UOM': Warehouse_goods_info.objects.get(pk=goods_qr_id).wh_uom,
              'L': Warehouse_goods_info.objects.get(pk=goods_qr_id).wh_goods_length,
              'W': Warehouse_goods_info.objects.get(pk=goods_qr_id).wh_goods_width,
              'H': Warehouse_goods_info.objects.get(pk=goods_qr_id).wh_goods_height,
              'first_name': first_name
              }
    qr = qrcode.QRCode()
    qr.add_data(img)
    qr.make()
    img_1 = qr.make_image()
    img_1.save('media/img.png')

    return render(request, "asset_mgt_app/goods_qr_code.html", context=context)
