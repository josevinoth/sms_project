import qrcode
import qrcode.image.svg
from io import BytesIO
from django.shortcuts import render, get_object_or_404
from ..models import AssetInfo

from django.shortcuts import render, get_object_or_404
import qrcode
from io import BytesIO
import base64

def qr_code_asset(request, asset_qr_id):
    # Fetch asset data or return 404 if not found
    asset = get_object_or_404(AssetInfo, pk=asset_qr_id)

    # Generate QR code with asset details
    qr_data = f"""
        Asset Number: {asset.asset_number}
        Assigned To: {asset.asset_assignedto}
        Location: {asset.asset_location}
        Product: {asset.asset_product}
        Asset ID: {asset.asset_Id}
    """
    qr = qrcode.QRCode(box_size=3, border=1)
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Save QR code to a PNG image in base64 format
    buffer = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(buffer)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    # Pass asset details and QR code to the template
    context = {
        "qr_code": f"data:image/png;base64,{qr_code_base64}",
        "Asset_Number": asset.asset_number,
        "Asset_Assigned_To": asset.asset_assignedto,
        "Asset_Location": asset.asset_location,
        "Asset_Product": asset.asset_product,
        "Asset_ID": asset.asset_Id,
    }
    return render(request, "asset_mgt_app/qr_code.html", context)


