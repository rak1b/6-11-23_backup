from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from coreapp.models import User, Document
from django.db.models import Model
import os
from django.conf import settings
from coreapp.helper import print_log
from PIL import Image
def create_dashboard_notification(sender, instance, created, *args, **kwargs):
    if created:
        from utility.models import DashboardNotification
        create_user_obj = DashboardNotification.objects.create(user_id=instance.id)

post_save.connect(create_dashboard_notification, sender=User)

# @receiver(post_save, sender=Document)
def document_post_save(sender, instance, **kwargs):
    if instance.doc_type == 0 and instance.document:
        try:
            post_save.disconnect(document_post_save, sender=Document)
            target_width = 100
            target_height = 100
            image = Image.open(instance.document.path)

            # Calculate the number of horizontal and vertical chunks
            num_horizontal_chunks = (image.width + target_width - 1) // target_width
            num_vertical_chunks = (image.height + target_height - 1) // target_height

            # Create a directory for resized images if it doesn't exist
            resized_dir = os.path.join(settings.MEDIA_ROOT, 'documents', 'resized')
            os.makedirs(resized_dir, exist_ok=True)

            # Initialize a list to hold the resized chunks with their order
            resized_chunks_with_order = []

            for i in range(num_horizontal_chunks):
                for j in range(num_vertical_chunks):
                    # Calculate the coordinates of the current chunk
                    left = i * target_width
                    upper = j * target_height
                    right = min((i + 1) * target_width, image.width)
                    lower = min((j + 1) * target_height, image.height)

                    # Crop the current chunk
                    chunk = image.crop((left, upper, right, lower))

                    # Resize the chunk to the target dimensions
                    chunk = chunk.resize((target_width, target_height), Image.ANTIALIAS)

                    # Append the resized chunk to the list with order information
                    resized_chunks_with_order.append((chunk, j * num_horizontal_chunks + i))

            # Sort the chunks based on their order
            resized_chunks_with_order.sort(key=lambda x: x[1])

            # Create a new image by pasting the resized chunks together
            new_image = Image.new('RGB', (image.width, image.height))
            current_x, current_y = 0, 0

            for chunk, _ in resized_chunks_with_order:
                new_image.paste(chunk, (current_x, current_y))
                current_x += target_width
                if current_x >= image.width:
                    current_x = 0
                    current_y += target_height

            # Save the resized image to the `resize_document` field
            resized_path = os.path.join(resized_dir, os.path.basename(instance.document.name))
            new_image.save(resized_path)

            # Update the `resize_document` field with the resized image path
            instance.resize_document.name = os.path.relpath(resized_path, settings.MEDIA_ROOT)
            instance.save()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print_log(f"Error processing image: {e}")
        finally:
            post_save.connect(document_post_save, sender=Document)

