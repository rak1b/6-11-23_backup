from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from inventory.models import *
from django.db.models import Q
from django.db.models.signals import pre_delete

@receiver(pre_delete, sender=OutLetProducts)
def delete_related_outlet_variants(sender, instance, **kwargs):
    instance.outletVariant.all().delete()

@receiver(post_save, sender=Products)
def update_related_products(sender, instance, created, *args, **kwargs):
    if  instance.is_update_related :
        related_products = instance.get_related_products_in_depth

        for product in related_products:
            without_current_related_product = related_products.exclude(id=product.id)  
            product.related_products.clear()
            product.related_products.set(without_current_related_product)
            product.is_update_related = False
            product.save()

        instance.is_update_related = False
        instance.save()


# @receiver(post_save, sender=OutLetProducts)
# def update_product_stock(sender, instance, created, *args, **kwargs):
#     print("Update product stock signal started")
#     if created:
#         instance.product.stock -= instance.stock
#         instance.product.save()
#         for outletVariant in instance.outletVariant.all():
#             outletVariant.variant.stock -= outletVariant.stock
#             outletVariant.variant.save()
        


