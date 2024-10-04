import base64
import cv2
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from ..models import CameraImage
from io import BytesIO
from PIL import Image
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings


@login_required(login_url='login_page')
def capture_image(request, image_id=0):
    if request.method == 'GET':
        # If it's an edit, get the existing images, otherwise initialize a new form
        if image_id == 0:
            return render(request, 'asset_mgt_app/capture.html', {'local': settings.DEBUG})
        else:
            camera_images = CameraImage.objects.filter(pk=image_id)
            return render(request, 'asset_mgt_app/capture.html', {'camera_images': camera_images, 'local': settings.DEBUG})

    elif request.method == 'POST':
        if settings.DEBUG:  # If in debug mode, capture image using OpenCV (local capture)
            try:
                # Initialize OpenCV and capture images locally
                camera = cv2.VideoCapture(0)
                captured_images = []

                # Capture multiple images, e.g., 3 images
                for _ in range(3):
                    ret, frame = camera.read()

                    if not ret:
                        messages.error(request, 'Failed to capture image')
                        return redirect('capture_image')

                    # Convert image to PIL format
                    image_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                    # Save image to a BytesIO buffer
                    buffer = BytesIO()
                    image_pil.save(buffer, format="JPEG")
                    image_content = ContentFile(buffer.getvalue())

                    captured_images.append(image_content)

                # Release the camera after capturing
                camera.release()

                # Save the captured images in the Django model
                for image_content in captured_images:
                    camera_image = CameraImage()  # New image instance
                    camera_image.image.save('captured_image.jpg', image_content)
                    camera_image.save()

                messages.success(request, 'Images saved successfully')
                return redirect('image_list')

            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                return render(request, 'asset_mgt_app/capture.html')

        else:  # In production, capture image using client-side webcam (base64 capture)
            try:
                # Get the base64 image data from the POST request (from the form submission)
                image_data = request.POST.get('image-data')
                if not image_data:
                    messages.error(request, 'No image data received.')
                    return redirect('capture_image')

                # Decode the base64 image data
                format, imgstr = image_data.split(';base64,')  # Split the format and the actual image data
                ext = format.split('/')[-1]  # Extract the file extension (e.g., jpeg)
                image_content = ContentFile(base64.b64decode(imgstr), name=f'captured_image.{ext}')

                # Save the image to the CameraImage model
                camera_image = CameraImage()
                camera_image.image.save(f'captured_image.{ext}', image_content)
                camera_image.save()

                messages.success(request, 'Image saved successfully')
                return redirect('image_list')

            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                return redirect('capture_image')


@login_required(login_url='login_page')  # Login required to view the image list
def image_list(request):
    images = CameraImage.objects.all()
    return render(request, 'asset_mgt_app/image_list.html', {'images': images})


@login_required(login_url='login_page')  # Login required to delete images
def image_delete(request, image_id):
    try:
        image = CameraImage.objects.get(pk=image_id)
        image.delete()
        messages.success(request, 'Image deleted successfully')
    except CameraImage.DoesNotExist:
        messages.error(request, 'Image not found')

    return redirect('image_list')
