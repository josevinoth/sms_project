from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.contrib import messages
from ..models import CameraImage  # Ensure you have imported your model
import base64
from django.contrib.auth.decorators import login_required

@login_required(login_url='login_page')
def capture_image(request, image_id=0):
    if request.method == 'GET':
        camera_images = CameraImage.objects.filter(pk=image_id) if image_id != 0 else None
        damagereport_id = request.session.get('ses_damagereport_id')
        print('damagereport_id', damagereport_id)
        return render(request, 'asset_mgt_app/capture.html', {
            'camera_images': camera_images,
            'damagereport_id': damagereport_id
        })

    elif request.method == 'POST':
        try:
            # Get the base64 image data from the POST request
            image_data = request.POST.get('image-data')
            if not image_data:
                messages.error(request, 'No image data received.')
                return redirect('capture_image')

            # Check if image_data contains 'base64,' to avoid errors
            if 'base64,' not in image_data:
                messages.error(request, 'Invalid image format.')
                return redirect('capture_image')

            # Decode the base64 image data
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_content = ContentFile(base64.b64decode(imgstr), name=f'captured_image.{ext}')

            # Get damagereport_id from session
            damagereport_id = request.session.get('ses_damagereport_id')
            if not damagereport_id:
                messages.error(request, 'No damagereport ID found in session.')
                return redirect('capture_image')

            # Save the image to the CameraImage model with the reference to damagereport_id
            camera_image = CameraImage()
            camera_image.image.save(f'captured_image.{ext}', image_content)
            camera_image.reference_id = damagereport_id
            camera_image.save()

            messages.success(request, 'Image saved successfully.')
            # return redirect('damage_report_detail', damagereport_id=damagereport_id)  # Redirect back to the damage report page
            url = 'damagereport_update/' + str(damagereport_id)
            return redirect(url)

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('capture_image')



@login_required(login_url='login_page')
def image_list(request):
    images = CameraImage.objects.all()

    capture_image(request)
    return render(request, 'asset_mgt_app/capture_image_list.html', {'images': images})


@login_required(login_url='login_page')
def image_delete(request, image_id):
    try:
        image = CameraImage.objects.get(pk=image_id)
        image.delete()
        messages.success(request, 'Image deleted successfully')
    except CameraImage.DoesNotExist:
        messages.error(request, 'Image not found')

    return redirect('image_list')
