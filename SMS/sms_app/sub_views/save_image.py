# views.py
from django.shortcuts import render
from django.http import JsonResponse
from .models import CapturedImage

def save_image(request):
    if request.method == 'POST':
        image_data = request.POST.get('image_data')
        # Save the image data to the database or file system
        # Example: CapturedImage.objects.create(image_data=image_data)
        return JsonResponse({'message': 'Image saved successfully.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)
