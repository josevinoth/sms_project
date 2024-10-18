from django.contrib.auth.decorators import login_required
from ..forms import pictureForm
from ..models import PictureImage, DamagereportInfo
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.base import ContentFile
import base64

@login_required(login_url='login_page')
def picture_add(request, picture_id=0):
    first_name = request.session.get('first_name')
    damagereport_id = request.session.get('ses_damagereport_id')  # Retrieve the damage report ID from the session

    if request.method == "GET":

        # When getting the form, either initialize it empty or with an existing image.
        if picture_id == 0:
            form = pictureForm()
        else:
            try:
                picture = PictureImage.objects.get(pk=picture_id)
                form = pictureForm(instance=picture)
            except PictureImage.DoesNotExist:
                messages.error(request, 'Image not found.')
                return redirect('/SMS/picture_list')  # Redirect if the image does not exist

        return render(request, "asset_mgt_app/picture.html", {
            'form': form,
            'first_name': first_name,
            'damagereport_id': damagereport_id,  # Pass the damage report ID to the template
        })

    else:
        try:
            # Handle form submission
            if picture_id == 0:
                form = pictureForm(request.POST)
            else:
                picture = PictureImage.objects.get(pk=picture_id)
                form = pictureForm(request.POST, instance=picture)

            # Capture and save base64 image if provided
            image_data = request.POST.get('image-data')
            if image_data:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                image_content = ContentFile(base64.b64decode(imgstr), name=f'picture.{ext}')

                # Save image if form is valid
                if form.is_valid():
                    saved_picture = form.save(commit=False)  # Save the form but don't commit yet
                    saved_picture.pi_image.save(f'picture.{ext}', image_content)  # Save the captured image

                    # Associate the picture with the specific damage report
                    if damagereport_id:
                        damagereport = DamagereportInfo.objects.get(pk=damagereport_id)
                        saved_picture.damagereport = damagereport  # Associate the image with the damage report

                    saved_picture.save()  # Now save the form
                    messages.success(request, 'Record and Image Saved Successfully')
                else:
                    messages.error(request, 'Error in saving the form: ' + str(form.errors))
            else:
                # If no image data is provided and the image field is empty, raise an error
                if form.is_valid():
                    saved_picture = form.save(commit=False)
                    if not saved_picture.pi_image:  # If no image is provided or exists
                        messages.error(request, 'An image is required.')
                    else:
                        # Associate the picture with the damage report
                        if damagereport_id:
                            damagereport = DamagereportInfo.objects.get(pk=damagereport_id)
                            saved_picture.damagereport = damagereport

                        saved_picture.save()
                        messages.success(request, 'Record Saved Successfully')
                else:
                    messages.error(request, 'Error in saving the form: ' + str(form.errors))

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

        return redirect('/SMS/picture_list')

# List View
@login_required(login_url='login_page')
def picture_list(request):
    first_name = request.session.get('first_name')
    pictures = PictureImage.objects.all()  # Fetch all the pictures
    context = {
        'picture_list': pictures,
        'first_name': first_name
    }
    return render(request, "asset_mgt_app/picture_list.html", context)

# Delete View
@login_required(login_url='login_page')
def picture_delete(request, picture_id):
    try:
        picture = PictureImage.objects.get(pk=picture_id)
        picture.delete()
        messages.success(request, 'Image deleted successfully')
    except PictureImage.DoesNotExist:
        messages.error(request, 'Image not found')
    return redirect('/SMS/picture_list')
