from django.contrib.auth.decorators import login_required
from ..forms import AssetinfoaddForm
from ..models import Warehouse_goods_info
from django.shortcuts import render, redirect
import cv2
from pyzbar.pyzbar import decode
import numpy as np

def goods_check(request,goods_id):
    first_name = request.session.get('first_name')
    goods_qr_id = {
        Warehouse_goods_info.objects.get(pk=goods_id).wh_goods_invoice,
        Warehouse_goods_info.objects.get(pk=goods_id).wh_goods_package_type
    }
    Cap = cv2.VideoCapture(0)
    Cap.set(3, 640)
    Cap.set(4, 480)
    while True:
        success, img = Cap.read()
        for barcode in decode(img):
            mydata = barcode.data.decode('utf-8')
            print(barcode.type)
            print(barcode.rect)
            pts = np.array([barcode.polygon], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(img, [pts], True, (255, 0, 255), 5)
            pts2 = barcode.rect
            cv2.putText(img, mydata, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)
        cv2.imshow('Result', img)
        cv2.waitKey(10)
