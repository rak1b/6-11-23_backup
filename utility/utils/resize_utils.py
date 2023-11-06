from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from coreapp.helper import print_log

def resize_image(document_memory_upload_format, width=500, height=500):
    try:
        document_name = document_memory_upload_format.name
        image = Image.open(document_memory_upload_format)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = image.resize((width, height), Image.Resampling.BILINEAR)
        buffer = BytesIO()
        image.save(buffer, format='WEBP')
        resized_image_file = InMemoryUploadedFile(
            buffer,
            None,  # Field name (use None or specify the field name)
            f"resized_{document_name}",  # File name
            'image/WEBP',  # Content type
            buffer.tell(),
            None  # Content type extra headers (optional)
        )

        return resized_image_file
    except Exception as e:
        print_log(f"Error resizing image: {str(e)}")
        return None
    

def get_data_bounding_box(image):
        width, height = image.size

        left, top, right, bottom = width, height, 0, 0

        for y in range(height):
            for x in range(width):
                pixel_color = image.getpixel((x, y))

                if pixel_color != (255, 255, 255):
                    left = min(left, x)
                    top = min(top, y)
                    right = max(right, x)
                    bottom = max(bottom, y)

        return left-10, top-10, right+10, bottom+10

