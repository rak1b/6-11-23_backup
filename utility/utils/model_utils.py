import math
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
import qrcode
from PIL import Image, ImageDraw
from decimal import Decimal
# def reupload_excel(filepath, model, model_mapping):

import json
import traceback
from openpyxl import load_workbook
from openpyxl_image_loader import SheetImageLoader
from openpyxl import load_workbook
import datetime
import pathlib
import uuid
from django.conf import settings
import string
import random
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from coreapp.pagination import paginate
from django.template.loader import render_to_string
from weasyprint import HTML
from pdf2image import convert_from_bytes
import os
from utility.utils.resize_utils import get_data_bounding_box
import base64
from utility.utils.bar_image_utils import Generate_barcode_modified
class FilterGivenDate(viewsets.ModelViewSet):
    @paginate
    @action(detail=False, methods=['get'])
    def filter(self, request, *args, **kwargs):
        start = request.GET.get("start")
        end = request.GET.get("end")
        try:
            start_month, start_day,  start_year = start.split("/")
        except:
            return Response({"data": [], "error": "Start date is empty or Please use correct format,month/date/year"}, status=status.HTTP_404_NOT_FOUND)
        try:
            end_month, end_day,  end_year = end.split("/")
        except:
            return Response({"data": [], "error": "End date is empty or Please use correct format,month/date/year"}, status=status.HTTP_404_NOT_FOUND)
        start_date = datetime.datetime(year=int(start_year), month=int(start_month), day=int(start_day),
                                        hour=0, minute=0, second=0)  # represents 00:00:00
        end_date = datetime.datetime(year=int(end_year), month=int(end_month), day=int(end_day),
                                        hour=23, minute=59, second=59)
        return self.queryset.model.objects.filter(created_at__range=[start_date, end_date])




def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    import uuid
    if new_slug is not None:
        slug = new_slug
    else:
        try:
            slug = slugify(instance.name)
        except:
            try:
                slug = slugify(instance.number)
            except:
                slug = slugify(str(uuid.uuid4()))

    Klass = instance.__class__
    max_length = Klass._meta.get_field('slug').max_length
    slug = slug[:max_length]
    qs_exists = Klass.objects.filter(slug=slug).exists()

    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug[:max_length-5], randstr=random_string_generator(size=4))

        return unique_slug_generator(instance, new_slug=new_slug)
    return slug




def generate_barcode(self, generated_bar_text):
    try:
        EAN = barcode.get_barcode_class('code128')
        ean = EAN(f"{generated_bar_text}", writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)
        self.barcode.save(f"{generated_bar_text}.png",
                        File(buffer), save=False)
    except Exception as e:
        import traceback
        traceback.print_exc()

def generate_product_barcode_modified_from_html(self):
    try:
        if self.barcode:
            barcode_image = self.barcode.read()  
            barcode_base64 = base64.b64encode(barcode_image).decode("utf-8")
            context = {
                "product": self,
                "barcode_base64": barcode_base64,
                "product_first_name": self.name[:30],
                "product_last_name": self.name[30:60],

            }
            html_string = render_to_string('invoice/barcode.html', context)
            try:
                pdf_buffer = BytesIO()
                HTML(string=html_string).write_pdf(pdf_buffer)
                pdf_images = convert_from_bytes(pdf_buffer.getvalue())

                if pdf_images:
                    image = pdf_images[0]
                    left, top, right, bottom = get_data_bounding_box(image)
                    cropped_image = image.crop((left, top, right, bottom))
                    image_buffer = BytesIO()
                    cropped_image.save(image_buffer, format='PNG')
                    image_buffer.seek(0)
                    self.barcode_modified.save(f"{self.sku}.png", File(image_buffer), save=False)
            except Exception as e:
                import traceback
                traceback.print_exc()
    except Exception as e:
        import traceback
        traceback.print_exc()


def generate_product_barcode(self):
    try:
        EAN = barcode.get_barcode_class('code128')
        ean = EAN(f"{self.sku}", writer=ImageWriter())  # Adjust the module_width as needed
        buffer = BytesIO()
        options = {'module_width': 0.8,'module_height': 30}
        ean.write(buffer, text='', options=options)
        self.barcode.save(f"{self.sku}.tiff", File(buffer), save=False)

        # image = Image.open(buffer)
        # new_width = 300  # Set the desired width
        # new_height = 100  # Set the desired height
        # resized_image = image.resize((new_width, new_height))
        # resized_buffer = BytesIO()
        # resized_image.save(resized_buffer, format='PNG')
        # resized_buffer.seek(0)
        # self.barcode.save(f"{self.sku}.png", File(resized_buffer), save=False)
        # price = f"{int(self.price)} BDT"
        # image_modified=add_images_and_text(price,self.name,self.sku,self.barcode.path) #With pillow
        
    except Exception as e:
        import traceback
        from coreapp.helper import print_log
        error_text = f"Error in generate_product_barcode:  \n {traceback.format_exc()}"
        print_log(error_text)

        

# def get_code(model_name, prefix="MB"):
#     obj = model_name.objects.order_by('-id').first()
#     prev_id = 0 if obj is None else obj.id
#     current_id = int(prev_id) + 1
#     return f"{prefix}{str(current_id).zfill(6)}"
def get_invoice_code(model_name, prefix="MB"):
    obj = model_name.objects.order_by('-id').first()
    prev_id = 0 if obj is None else obj.id
    current_id = int(prev_id) + 1
    code = f"{prefix}{str(current_id).zfill(6)}"
    
    # Check for duplicates and fix if necessary
    while model_name.objects.filter(number=code).exists():
        current_id += 1
        code = f"{prefix}{str(current_id).zfill(6)}"
    
    return code

def get_code(model_name, prefix="MB"):
    obj = model_name.objects.order_by('-id').first()
    prev_id = 0 if obj is None else obj.id
    current_id = int(prev_id) + 1
    code = f"{prefix}{str(current_id).zfill(6)}"
    
    # Check for duplicates and fix if necessary


def generate_qrcode(self, text):
    text = text.replace("https://", "").replace("http://", "")
    qrcode_img = qrcode.make(text)
    size = qrcode_img.size
    canvas = Image.new('RGB', size, 'white')
    canvas.paste(qrcode_img)
    fname = f'qr_code-{text}.png'
    buffer = BytesIO()
    canvas.save(buffer, 'PNG')
    self.qr_code.save(fname, File(buffer), save=False)
    canvas.close()


from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
import datetime
from coreapp.pagination import paginate




class FilterGivenDateInvoice(viewsets.ModelViewSet):
    @paginate
    @action(detail=False, methods=['get'])
    def filter(self, request, *args, **kwargs):
        start = request.GET.get("start")
        end = request.GET.get("end")
        try:
            start_month, start_day,  start_year = start.split("/")
        except:
            return Response({"data": [], "error": "Start date is empty or Please use correct format,month/date/year"}, status=status.HTTP_404_NOT_FOUND)
        try:
            end_month, end_day,  end_year = end.split("/")
        except:
            return Response({"data": [], "error": "End date is empty or Please use correct format,month/date/year"}, status=status.HTTP_404_NOT_FOUND)
        start_date = datetime.datetime(year=int(start_year), month=int(start_month), day=int(start_day),
                                        hour=0, minute=0, second=0)  # represents 00:00:00
        end_date = datetime.datetime(year=int(end_year), month=int(end_month), day=int(end_day),
                                        hour=23, minute=59, second=59)
        return self.get_queryset().model.objects.filter(invoice_date__range=[start_date, end_date])
    


def generate_resize():
    from inventory.models import Products
    from coreapp.models import Document
    products = Products.objects.all()
    docs = products.values_list("thumb", flat=True)
    docs2 = products.values_list("thumb2", flat=True)
    docs = list(docs)
    docs2 = list(docs2)
    docs.extend(docs2)
    docs = list(set(docs))
    print(len(docs))
    # try:
    #     for doc in docs:
    #         try:
    #             doc = Document.objects.get(pk=doc)
    #         except:
    #             continue
    #         doc.height = 600
    #         doc.width = 600
    #         doc.save()
    # except Exception as e:
    #     import traceback
    #     from coreapp.helper import print_log
    #     traceback.print_exc()
    #     print_log(f"Error in generate_resize:  \n {traceback.format_exc()}")
    # print("done")

# from utility.utils.model_utils import generate_resize


def get_1mb():
    from inventory.models import Products
    import os
    from django.db.models import Q

    # Define the size limit (in megabytes) for documents greater than 1MB
    size_limit_mb = 1  # 1MB

    # Open a text file for writing
    with open('products_with_large_thumb.txt', 'w') as output_file:
        # Query products with large thumb1 or thumb2 images
        products_with_large_thumb = Products.objects.filter(
            Q(thumb__isnull=False) | Q(thumb2__isnull=False)
        )

        # Check the size of thumb1 or thumb2 and write to the text file
        for product in products_with_large_thumb:
            thumb_size_mb = None
            thumb_name = None
            
            if product.thumb and product.thumb.document:
                thumb_size_bytes = os.path.getsize(product.thumb.document.path)
                thumb_size_mb = thumb_size_bytes / (1024 * 1024)  # Convert to MB
                thumb_name = 'thumb1'
            elif product.thumb2 and product.thumb2.document:
                thumb_size_bytes = os.path.getsize(product.thumb2.document.path)
                thumb_size_mb = thumb_size_bytes / (1024 * 1024)  # Convert to MB
                thumb_name = 'thumb2'
            
            if thumb_size_mb is not None and thumb_size_mb > size_limit_mb:
                output_file.write(f"Product Name: {product.name}, SKU: {product.sku}, {thumb_name} Size: {thumb_size_mb:.2f} MB\n")

# from utility.utils.model_utils import *
# get_1mb()


def bar_from_terminal():
    from inventory.models import Products
    products = Products.objects.all()
    for product in products:
        product.save()
        print(product.name)
    
    print("done")



def category_random_order():
    from inventory.models import Category
    category = Category.objects.all().update(order=random.randint(10000000, 99999999))

