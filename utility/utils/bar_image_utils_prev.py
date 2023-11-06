from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import uuid,os
from coreapp.helper import print_log

image_path = rf"{settings.MEDIA_ROOT}/bar_codes/base/white4.png"
output_path = rf"{settings.MEDIA_ROOT}/bar_codes/base/out/out.png"
font_path = rf"{settings.MEDIA_ROOT}/bar_codes/base/font/arial_bold.ttf"

# print_log("test_path" + image_path + " " + output_path)
image_path = r"H:\Devsstream_NEW\kaaruj-backend-v2\media\bar_codes\products\base\white4.png"
output_path = r"H:\Devsstream_NEW\kaaruj-backend-v2\media\bar_codes\products\base\out\out.png"
font_path = r"H:\Devsstream_NEW\kaaruj-backend-v2\media\bar_codes\products\base\font\arial_bold.ttf"
def insert_text(image_path, text, output_path, size, add_x=0, position_y=0,color=0):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font_size = size
    font = ImageFont.truetype(font_path, font_size)
    image_width, image_height = image.size
    print(image_width, image_height)
    # text_width, text_height = draw.textsize(text, font=font)
    bbox = draw.textbbox((0, position_y), text, font=font, anchor="lt")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position_x = (image_width - text_width) / 2 + add_x
    position = (position_x, position_y)
    text_color = color
    draw.text(position, text, font=font, fill=text_color)
    image.save(output_path)

    return image


def insert_image(image_path, inserted_image_path, output_path, position_y):
    background_image = Image.open(image_path)
    inserted_image = Image.open(inserted_image_path)
    position_x = (background_image.width - inserted_image.width) // 2
    position = (position_x, position_y)
    background_image.paste(inserted_image, position)
    background_image.save(output_path)
    return background_image

# Example usage

def resize_image_barcode(input_image_path, output_image_path, new_height, new_width):
    image = Image.open(input_image_path)
    width, height = image.size
    aspect_ratio = float(width) / float(height)
    new_width = int(aspect_ratio * new_height)
    resized_image = image.resize((new_width, new_height))
    resized_image.save(output_image_path)


def add_images_and_text(price,product_name,sku,generated_barcode_path):
    try:
        text = price
        text2 = product_name[:24]
        text3 = sku
        # insert_position = (10, 120)  # Position to insert the image
        modified_image = insert_text(image_path, text, output_path, size=25, add_x=0, position_y=100,color='black')
        modified_image = insert_text(output_path, text2, output_path, size=30, add_x=0, position_y=155,color='black')
        modified_image = insert_text(output_path, text3, output_path, size=30, add_x=0, position_y=305,color='black')
        insert_image(output_path, generated_barcode_path, generated_barcode_path, 195)
        # resize_image_barcode(generated_barcode_path, generated_barcode_path, 200, 195)
        return modified_image
    except Exception as e:
        import traceback
        from coreapp.helper import print_log
        error_text = f"Error in generate_product_barcode:  \n {traceback.format_exc()}"
        print_log(error_text)
# add_images_and_text(text,text2,text3,inserted_image_path)
