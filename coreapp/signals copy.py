from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from coreapp.models import User, Document
from PIL import Image
from django.db.models import Model
import os
from django.conf import settings
from coreapp.helper import print_log

def create_dashboard_notification(sender, instance, created, *args, **kwargs):
    if created:
        from utility.models import DashboardNotification
        create_user_obj = DashboardNotification.objects.create(user_id=instance.id)

post_save.connect(create_dashboard_notification, sender=User)

def document_post_save(sender, instance, **kwargs):
    if instance.doc_type == 0 and instance.document:
        try:
            post_save.disconnect(document_post_save, sender=Document)
            
            # Extract the original image filename without extension
            from django.conf import settings
            base_dir = settings.BASE_DIR
            file_name_without_extension = os.path.splitext(instance.document.name)[0]
            resize_jpg_path =  f"{base_dir}/media/{file_name_without_extension}_resize.webp"
            
            target_width = 500  # Adjust to your desired width
            target_height = 500  # Adjust to your desired height
            original_image = Image.open(instance.document.path)
            num_chunks_width = int(original_image.width / target_width)
            num_chunks_height = int(original_image.height / target_height)
            resized_image = Image.new("RGB", (original_image.width, original_image.height))
            for i in range(num_chunks_width):
                for j in range(num_chunks_height):
                    left = i * target_width
                    upper = j * target_height
                    right = (i + 1) * target_width
                    lower = (j + 1) * target_height
                    chunk = original_image.crop((left, upper, right, lower))
                    chunk = chunk.resize((target_width, target_height))
                    resized_image.paste(chunk, (left, upper))
            resized_image.save(resize_jpg_path, "WEBP")
            original_image.close()
            resized_image.close()
            instance.resize_document = resize_jpg_path
            instance.save()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print_log(f"Error processing image: {e}")
        finally:
            post_save.connect(document_post_save, sender=Document)
