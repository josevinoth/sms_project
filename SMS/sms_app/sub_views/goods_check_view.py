from django.contrib.auth.decorators import login_required
from ..forms import AssetinfoaddForm
from ..models import Warehouse_goods_info
from django.shortcuts import render, redirect
import cv2
# from pyzbar.pyzbar import decode
import numpy as np

qr_detector = cv2.QRCodeDetector()


@login_required(login_url='login_page')
def goods_check(request, goods_id):
    first_name = request.session.get('first_name')

    goods = Warehouse_goods_info.objects.get(pk=goods_id)
    goods_qr_id = {
        goods.wh_goods_invoice,
        goods.wh_goods_package_type
    }

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        success, img = cap.read()
        if not success:
            break

        # ✅ OpenCV QR Decode
        data, points, _ = qr_detector.detectAndDecode(img)

        if data:
            mydata = data.strip()
            print("QR DATA:", mydata)

            if points is not None:
                # points shape: (1, 4, 2) → convert to (4, 2)
                pts = points[0].astype(int)

                # ✅ Draw bounding box
                cv2.polylines(img, [pts], True, (255, 0, 255), 5)

                # ✅ Text position
                text_x, text_y = pts[0][0], pts[0][1] - 10
                if text_y < 10:
                    text_y = pts[0][1] + 20

                cv2.putText(
                    img,
                    mydata,
                    (int(text_x), int(text_y)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (255, 0, 255),
                    2
                )

        cv2.imshow('Result', img)

        # ESC key to exit
        if cv2.waitKey(10) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return redirect(request.META.get('HTTP_REFERER', '/'))
