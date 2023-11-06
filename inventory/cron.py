import random
from django.db import transaction
from inventory.models import Products
from django.db.models import F


def set_random_order_for_all_products():
    products = Products.objects.all()
    max_limit = products.count()
    with transaction.atomic():
        for product in products:
            product.order = random.random() * max_limit
            product.save()


def UpdateProductOrder():
    Products.objects.update(order=F("id") * random.randint(1, 1000))
    print("Product order updated")

def test():
    from coreapp.helper import print_log
    from utility.models import Subscription
    Subscription.objects.create(email="New_email@gmail.com")
    print_log("-----------Cron Job Started-----------")


