from django.contrib.auth.decorators import login_required
from ..forms import AssetinfoaddForm
from ..models import AssetInfo
from django.shortcuts import render, redirect
import io
from reportlab.pdfgen import canvas
from django.http import FileResponse

@login_required(login_url='login_page')
def print_pdf(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 500, 'Asset_Number')

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='QR_Code.pdf')