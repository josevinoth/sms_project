import cv2
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from ..models import CameraImage
from io import BytesIO
from PIL import Image
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required(login_url='login_page')
def capture_image(request, image_id=0):
    if request.method == 'GET':
        # If it's an edit, get the existing images, otherwise initialize a new form
        if image_id == 0:
            return render(request, 'asset_mgt_app/capture.html')
        else:
            camera_images = CameraImage.objects.filter(pk=image_id)
            return render(request, 'asset_mgt_app/capture.html', {'camera_images': camera_images})

    elif request.method == 'POST':
        try:
            # Initialize OpenCV and capture images
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

            # Save or update the captured images in the Django model
            for image_content in captured_images:
                camera_image = CameraImage()  # New image instance
                camera_image.image.save('captured_image.jpg', image_content)
                camera_image.save()

            messages.success(request, 'Images saved successfully')
            return redirect('image_list')  # Redirect to the list of images after saving

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'asset_mgt_app/capture.html')


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
