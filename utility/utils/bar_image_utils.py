from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import io
from django.core.files import File
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import uuid,os
from coreapp.helper import print_log

from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse
from io import BytesIO
import io
from django.core.files import File
from django.core.files.base import ContentFile

def insert_text(image, text, size, position_y=0, color=(0, 0, 0)):
    font_path = rf"{settings.MEDIA_ROOT}/bar_codes/base/font/FreeSansBold.ttf"
    font_path_local = r"H:\Devsstream_NEW\kaaruj-backend-v2\media\bar_codes\products\base\font\FreeSansBold.ttf"

    draw = ImageDraw.Draw(image)
    font_size = size
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.truetype(font_path_local, font_size)

    bbox = draw.textbbox((0, position_y), text, font=font, anchor="lt")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    image_width, _ = image.size
    position_x = (image_width - text_width) / 2
    position = (position_x, position_y)
    draw.text(position, text, font=font, fill=color)

def Generate_barcode_modified(product):
    try:
        # width, height = 500, 350
        width, height = 2000, 1400  # Increase the width and height for higher resolution
        background_color = (255, 255, 255)
        image = Image.new("RGB", (width, height), background_color)

        start_y = 50
        logo_data =  {"text": "KAARUJ", "font_size": 200, "position_y": start_y}

        price_data = {"text": f"{int(product.price)} BDT (vat included)", "font_size":125, "position_y":logo_data["position_y"]+5+logo_data["font_size"]}

        # vat_data = {"text": "", "font_size": 18, "position_y": price_data["position_y"]+8+price_data["font_size"]}

        name_data = {"text": product.name[:30], "font_size": 125, "position_y": price_data["position_y"]+10+price_data["font_size"]}
        name_data_last = {"text":f"{product.name[30:60]}", "font_size": 125, "position_y": name_data["position_y"]+2+name_data["font_size"]}

        if len(product.name) < 30:
            barcode_img_data = {"path": product.barcode.path,"font_size": 280, "position_y": name_data["position_y"]+25+name_data["font_size"]}
        else:
            barcode_img_data = {"path": product.barcode.path,"font_size": 280, "position_y": name_data_last["position_y"]+35+name_data_last["font_size"]}

        sku_data = {"text": product.sku , "font_size": 125, "position_y": barcode_img_data["position_y"] + barcode_img_data["font_size"]+260}

        if len(product.name) < 30:
            text_data = [logo_data,price_data,name_data, sku_data]
        else:
            text_data = [logo_data,price_data,name_data,name_data_last, sku_data]

        for item in text_data:
            insert_text(image, item["text"], item["font_size"], position_y=item["position_y"])

        barcode_image = Image.open(barcode_img_data['path'])
        new_width = width - 100
        new_height = int(barcode_img_data["font_size"] * 2)
        barcode_image = barcode_image.resize((new_width, new_height), Image.LANCZOS)
        barcode_position_x = (width - barcode_image.width) // 2
        barcode_position_y = barcode_img_data['position_y']
        image.paste(barcode_image, (barcode_position_x, barcode_position_y))

        image_buffer = io.BytesIO()
        image.resize((500, 350), Image.LANCZOS)
        image.save(image_buffer, format="png")  
        image_buffer.seek(0)
        
        barcode_image = File(image_buffer)
        unique_filename = f"barcode_{uuid.uuid4()}.png"
        product.barcode_modified.save(unique_filename, barcode_image,save=False)

    except Exception as e:
        import traceback
        print_log(f"Error in generate_product_barcode: \n{traceback.format_exc()}")
