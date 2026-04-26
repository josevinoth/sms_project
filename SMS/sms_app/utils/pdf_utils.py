import io
from django.core.files.base import ContentFile

def merge_pdf_files(file_fields, output_name):
    """
    Generic utility to merge PDF and image files from Django FileFields into a single PDF.
    Returns a tuple (bool, ContentFile or None)
    """
    IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp')
    has_any = False

    try:
        from pypdf import PdfWriter, PdfReader
        writer = PdfWriter()

        for file_field in file_fields:
            if not file_field or not file_field.name:
                continue
            try:
                file_field.open('rb')
                content = file_field.read()
                file_field.close()
                fname = file_field.name.lower()

                if fname.endswith('.pdf'):
                    reader = PdfReader(io.BytesIO(content))
                    for page in reader.pages:
                        writer.add_page(page)
                    has_any = True

                elif fname.endswith(IMAGE_EXTS):
                    from PIL import Image
                    img = Image.open(io.BytesIO(content))
                    if img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')
                    img_pdf_buf = io.BytesIO()
                    img.save(img_pdf_buf, format='PDF')
                    img_pdf_buf.seek(0)
                    reader = PdfReader(img_pdf_buf)
                    for page in reader.pages:
                        writer.add_page(page)
                    has_any = True

            except Exception as e:
                print(f"Error processing field {file_field}: {e}")

        if has_any:
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            return True, ContentFile(output.read(), name=output_name)
        
        return False, None

    except Exception as e:
        print(f"Merge function error: {e}")
        return False, None
