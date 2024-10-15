from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.contrib import messages
from ..models import DamagereportInfo,damage_image_type_info,CameraImage  # Ensure you have imported your model
import base64
from django.contrib.auth.decorators import login_required

@login_required(login_url='login_page')
def capture_image(request, image_id=0):
    if request.method == 'GET':
        damagereport_id = request.session.get('ses_damagereport_id')
        image_types = damage_image_type_info.objects.all()  # Fetch all image types to display in the dropdown
        print('Fetched image types:', list(image_types))  # Convert queryset to list for easier debugging
        return render(request, 'asset_mgt_app/capture.html', {
            'damagereport_id': damagereport_id,
            'image_types': image_types
        })

    elif request.method == 'POST':
        try:
            # Get the base64 image data from the POST request
            image_data = request.POST.get('image-data')
            if not image_data:
                messages.error(request, 'No image data received.')
                return redirect('capture_image')

            # Get the reference and image type from the POST data
            damagereport_id = request.POST.get('reference')
            image_type_id = request.POST.get('image_type')

            # Fetch the related damagereport and image type objects
            damagereport = DamagereportInfo.objects.get(pk=damagereport_id)
            image_type = damage_image_type_info.objects.get(pk=image_type_id)

            # Decode the base64 image data
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]  # Extract file extension (jpeg, png, etc.)
            image_content = ContentFile(base64.b64decode(imgstr), name=f'captured_image.{ext}')

            # Save the image to the CameraImage model
            camera_image = CameraImage(reference=damagereport, image_type=image_type)
            camera_image.image.save(f'captured_image.{ext}', image_content)
            camera_image.save()

            messages.success(request, 'Image saved successfully.')
            return redirect('damage_report_detail', damagereport_id=damagereport_id)

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
