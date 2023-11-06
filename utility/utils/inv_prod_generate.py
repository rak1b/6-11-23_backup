from django.core.management.base import BaseCommand

from .utils import setup_utils
from utility.utils.printer_utils import convert_zpl
from inventory.models import Products
from sales.models import *
import json
# website invoice count: 5 <QuerySet ['INV001230', 'INV001226', 'INV001207', 'INV001195', 'INV001194']
# print(f"website invoice count: {inv.filter(source=0).count()} {inv.filter(source=0).values_list('number',flat=True)}")

def create_invoice_products(invoice):
    product_list_json = json.loads(invoice.product_list_json)
    for product_name, product_data in product_list_json['mainstate'].items():
        product_id = product_data['id']
        for variant_name, variant_data in product_data['variantObj'].items():
            variant_id = variant_data['id']
            quantity = int(variant_data['quantity'])
            total = float(variant_data['total'])
            
            # Create an Invoice_Products instance for this product-variant combination
            if quantity > 0:
                invoice_product = Invoice_Products(
                    product_id=product_id,
                    variant_id=variant_id,
                    quantity=quantity,
                    total=total,
                    product_name=product_name,
                    variant_name=variant_name,
                    invoice_date = invoice.invoice_date
                )
                invoice_product.save()
                invoice.invoice_products.add(invoice_product)
    invoice.save()
    print("Regular Invoice Products Created")
def create_custom_invoice_products(invoice):
    product_list_json = json.loads(invoice.product_list_json)
    for product_name, product_data in product_list_json['mainstate'].items():
        for variant_name, variant_data in product_data['variantObj'].items():
            quantity = int(variant_data['quantity'])
            total = float(variant_data['total'])
            
            # Create an Invoice_Products instance for this product-variant combination
            if quantity > 0:
                invoice_product = Invoice_Products(
                    product_id=None,
                    variant_id=None,
                    quantity=quantity,
                    total=total,
                    product_name=product_name,
                    variant_name=variant_name,
                    invoice_date = invoice.invoice_date
                )
                invoice_product.save()
                invoice.invoice_products.add(invoice_product)
    invoice.save()

def create_website_invoice_products(invoice):
    car  = invoice.checkout.cart
    cart_items = car.item.all()
    for item in cart_items:
        invoice_product = Invoice_Products(
            product_id=item.product.id,
            variant_id=item.variant.id,
            quantity=item.quantity,
            total=item.get_subtotal(),
            product_name=item.product.name,
            variant_name=item.variant.name,
            invoice_date = invoice.invoice_date
        )
        invoice_product.save()
        invoice.invoice_products.add(invoice_product)
    invoice.save()
    print(f"invoice number: {invoice.number} cart items: {cart_items.count()}")
    

class Command(BaseCommand):
    help = 'Initial configuration and settings for application'

    def handle(self, *args, **kwargs):
        from sales.models import Invoice
        inv = Invoice.objects.filter(is_outlet=False,invoice_products=None)
        is_custom = inv.filter(is_custom=True)
        is_regular = inv.filter(is_regular=True,source=1)
        is_website = inv.filter(source=0)
        for inv in is_regular:
            create_invoice_products(inv)
        for inv in is_custom:
            try:
                print(f"generating custom invoice products {inv.number}")
                create_custom_invoice_products(inv)
            except:
                import traceback
                traceback.print_exc()
        for inv in is_website:
            create_website_invoice_products(inv)
        from sales.cron import createDailyReportManual
        createDailyReportManual(2023,10,26)
            # print(inv.product_list_json)
            

