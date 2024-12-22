import qrcode
import qrcode.image.svg
from io import BytesIO
from django.shortcuts import render
from ..models import AssetInfo

def qr_code_asset(request, asset_qr_id):
    # Fetch asset data once
    asset = AssetInfo.objects.get(pk=asset_qr_id)
    first_name = request.session.get('first_name')

    # Format data for the QR code
    qr_data = f"""
            Asset Number: {asset.asset_number}
            Assigned To: {asset.asset_assignedto}
            Location: {asset.asset_location}
            Product: {asset.asset_product}
            Asset ID: {asset.asset_Id}"""

    # Generate the QR code as SVG
    factory = qrcode.image.svg.SvgImage
    qr_img = qrcode.make(qr_data, image_factory=factory, box_size=8)

    # Save QR code to a stream
    stream = BytesIO()
    qr_img.save(stream)

    # Prepare context for the template
    context = {
        'svg': stream.getvalue().decode(),  # QR code in SVG format
        'Asset_Number': asset.asset_number,
        'Asset_Assigned_To': asset.asset_assignedto,
        'Asset_Location': asset.asset_location,
        'Asset_Product': asset.asset_product,
        'Asset_ID': asset.asset_Id,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/qr_code.html", context=context)

