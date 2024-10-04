import base64
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from ..models import CameraImage
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required(login_url='login_page')
def capture_image(request, image_id=0):
    if request.method == 'GET':
        # If it's an edit, fetch the existing images, otherwise render an empty form
        camera_images = CameraImage.objects.filter(pk=image_id) if image_id != 0 else None
        return render(request, 'asset_mgt_app/capture.html', {'camera_images': camera_images})

    elif request.method == 'POST':
        try:
            # Get the base64 image data from the POST request (sent from client-side)
            image_data = request.POST.get('image-data')
            if not image_data:
                messages.error(request, 'No image data received.')
                return redirect('capture_image')

            # Decode the base64 image data
            format, imgstr = image_data.split(';base64,')  # Split the format and the base64 image data
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


@login_required(login_url='login_page')
def image_list(request):
    images = CameraImage.objects.all()
    return render(request, 'asset_mgt_app/image_list.html', {'images': images})


@login_required(login_url='login_page')
def image_delete(request, image_id):
    try:
        image = CameraImage.objects.get(pk=image_id)
        image.delete()
        messages.success(request, 'Image deleted successfully')
    except CameraImage.DoesNotExist:
        messages.error(request, 'Image not found')

    return redirect('image_list')
