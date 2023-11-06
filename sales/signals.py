from fileinput import filename
import json
import traceback
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.signals import user_logged_in
from utility.utils.notification_utils import createNotifications
from sales.helpers import save_pdf, sendPdfEmail
from sales.models import Invoice, Invoice_Products,Chalan
from inventory.models import Variant, Products, Customer
from django.db.models import Q
from django.db.models.query import QuerySet
from coreapp.models import User
import time
from django.db.models.signals import pre_save
from userapp.models import Notifications
import asyncio
import threading
from rest_framework.serializers import ValidationError
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from decouple import config
from .helpers import get_invoice_params, SendEmailWithPDF
from coreapp.helper import print_log

def createCustomer(sender, instance, *args, **kwargs):
    try:
        mobile = instance.to_mobile
        address = instance.to_address

        findCustomer = Customer.objects.filter(mobile=mobile).first()

        if findCustomer == None:
            customer = Customer.objects.create(name=instance.bill_to, mobile=mobile,
                                            email=instance.to_email, status=True,
                                            to_address = instance.to_address,
                                            to_address2 = instance.to_address2,
                                            to_zip_code = instance.to_zip_code,
                                            to_city = instance.to_city,
                                            to_division = instance.to_division,
                                            to_district = instance.to_district,
                                            to_country = instance.to_country,
                                            redex_division = instance.redex_division,
                                            redex_district = instance.redex_district,
                                            redex_area = instance.redex_area,

                                            )
        else:  # user exists ,then have to update phone,address
            # findCustomer.total_purchase = total
            if findCustomer.to_address != address:
                findCustomer.to_address = address
                findCustomer.save()
            print("---------Customer updated from signal---------")
    except Exception as e:
        traceback.print_exc()
        print_log("---------Customer create/update issue---------")
        print_log(str(e))




def ReduceVariantStock(sender, instance, created, *args, **kwargs):
    print("---------Stock update from signal---------")
    print(f"created = {created} is regular = {instance.is_regular} is convert to regular = {instance.is_convert_to_regular}")
    if (created and instance.is_regular) or instance.is_convert_to_regular:
        try:
            product = instance.product
            variant = instance.variant
            quantity = instance.quantity if type(instance.quantity) == int else int(instance.quantity)
            if variant:
                if variant.stock >= quantity:
                    variant.stock -= quantity
                    variant.save()
                else:
                    raise ValidationError(f"Insufficient stock for variant: {variant}")
            if product:
                if product.stock >= quantity:
                    product.stock -= quantity
                    product.save()
                else:
                    raise ValidationError(f"Insufficient stock for product: {product}")
            if instance.is_convert_to_regular:
                instance.is_convert_to_regular = False
                instance.is_draft = False
                instance.save()
        except Exception as e:
            traceback.print_exc()
            print_log(f"---------Stock update issue---------  {traceback.format_exc()}")

    if created and instance.is_outlet:
        from inventory.models import OutLetProducts,OutletVariant
        from django.db.models import Sum
        try:
            outlet = instance.outlet
            product = instance.product
            variant = instance.variant
            outlet_product_list = OutLetProducts.objects.filter(outlet=outlet, product=product,is_return=False)
            outlet_variant_list = OutletVariant.objects.filter(outlet=outlet, variant=variant)
            total_avaialable_product_stock = outlet_product_list.aggregate(Sum('stock'))['stock__sum']
            total_avaialable_variant_stock = outlet_variant_list.aggregate(Sum('stock'))['stock__sum']
            product_reduce_quantity = instance.quantity if type(instance.quantity) == int else int(instance.quantity)
            variant_reduce_quantity = instance.quantity if type(instance.quantity) == int else int(instance.quantity)
            print_log(f'product_reduce_quantity {product_reduce_quantity} variant_reduce_quantity {variant_reduce_quantity} total avaialable product stock {total_avaialable_product_stock} total avaialable variant stock {total_avaialable_variant_stock}')
            for outlet_product in outlet_product_list: 
                        # 160                          60
                if total_avaialable_product_stock >= product_reduce_quantity and total_avaialable_product_stock > 0 and product_reduce_quantity > 0:
                    if outlet_product.stock >= product_reduce_quantity:
                        outlet_product.stock -= product_reduce_quantity
                        product_reduce_quantity = 0
                    else:
                        product_reduce_quantity = product_reduce_quantity - outlet_product.stock
                        outlet_product.stock = 0
                    outlet_product.save()

                    print_log(f"\n total_avaialable_product_stock {total_avaialable_product_stock} product_reduce_quantity {product_reduce_quantity} outlet_product.stock {outlet_product.stock} id {outlet_product.id} IN ELSE-- \n")

                else:
                    print_log(f"\n total_avaialable_product_stock {total_avaialable_product_stock} product_reduce_quantity {product_reduce_quantity} outlet_product.stock {outlet_product.stock} id {outlet_product.id} IN ELSE-- \n")
            for outlet_variant in outlet_variant_list:
                if total_avaialable_variant_stock >= variant_reduce_quantity and total_avaialable_variant_stock > 0 and variant_reduce_quantity > 0:
                    if outlet_variant.stock >= variant_reduce_quantity:
                        outlet_variant.stock -= variant_reduce_quantity
                        variant_reduce_quantity = 0
                    else:
                        variant_reduce_quantity = variant_reduce_quantity - outlet_variant.stock
                        outlet_variant.stock = 0
                    outlet_variant.save()
  
                    print_log(f"{outlet_variant.stock} id {outlet_product.id} outlet_product stock reduced-----------------\n")

                else:
                    print_log(f"\n total_avaialable_variant_stock {total_avaialable_variant_stock} variant_reduce_quantity {variant_reduce_quantity} outlet_variant.stock {outlet_variant.stock} id {outlet_variant.id} IN ELSE-- \n")
        except Exception as e:
            traceback.print_exc()
            print_log(f"---------Product Stock update issue outlet--------- {traceback.format_exc()}")







def send_stock_notifications(sender, instance, created, *args, **kwargs):
    try:
        name = instance.name
        stock = instance.stock
        if stock < 10:
            title = "Low Inventory"
            info = f'''<span class="fw-bold">{name}'s</span> stock is too <span class="fw-bold">low</span>! Current stock : {stock} </span>'''
            notification = Notifications.objects.create(title=title, info=info)

    except Exception as e:
        traceback.print_exc()
        print_log(f"---------Stock notification issue---------   {traceback.format_exc()} ")









        

def SavePdfAndSendMail(sender, instance, created, **kwargs):
    from_mail = config('EMAIL_SENDER')
    params = get_invoice_params(instance)
    subject = f'#{instance.number} - New Invoice Generated From kaaruj'
    message = ""
    print(f"senf pdf {instance.send_pdf} and send pdf admin {instance.send_pdf_admin} and invoice product count {instance.invoice_products.all().count()}")
    if  instance.send_pdf and instance.invoice_products.all().count() > 0:
        instance.send_pdf = False
        instance.save()
        to_mail = [instance.to_email]
        if instance.source == 0:
            to_mail.append(config('EMAIL_RECIEVER'))
        subject = f'#{instance.number} - Your order has been placed From KAARUJ'
        SendEmailWithPDF(subject, message,  from_mail, to_mail, params)
    # if instance.send_pdf_admin and instance.invoice_products.all().count() > 0:
    #     to_mail = [config('EMAIL_RECIEVER')]
    #     instance.send_pdf_admin = False
    #     instance.save()
    #     SendEmailWithPDF(subject, message,  from_mail, to_mail, params)




def UpdateProductOnReturn(sender, instance, created, **kwargs):
    try:
        inv_products = instance.get_invoice_products()
        if not created and instance.delivery_status==0 and instance.is_stock_updated_after_return==False and not instance.is_purchase_order and not instance.is_requisition_order and not instance.is_outlet:
            for inv_product in inv_products:
                try:
                    product = Products.objects.get(id=inv_product.product.id)
                    product.stock += inv_product.quantity
                    product.save()
                    variant = Variant.objects.get(id=inv_product.variant.id)
                    variant.stock += inv_product.quantity
                    variant.save()
                except Exception as e:
                    traceback.print_exc()
                    print_log(f"UpdateProductOnReturn_issue   {traceback.format_exc()}")
            instance.is_stock_updated_after_return = True
            instance.save()

        if not created and instance.is_outlet and instance.delivery_status==0 and instance.is_stock_updated_after_return==False:
            from inventory.models import OutLetProducts,OutletVariant
            outlet = instance.outlet
            for inv_product in inv_products:
                try:
                    product = OutLetProducts.objects.filter(outlet=outlet, product_id=inv_product.product.id,is_return=False).first()
                    print_log(f"outlet product {product}  invproduct {inv_product} quantity {inv_product.quantity}")
                    product.stock += inv_product.quantity
                    product.save()
                    variant = product.outletVariant.get(variant_id=inv_product.variant.id)
                    variant.stock += inv_product.quantity
                    variant.save()
                except Exception as e:
                    traceback.print_exc()
                    print_log(f"UpdateProductOutletOnReturn_issue {e}")
            print_log("Outlet product returned-----------------")
            
    except Exception as e:
        print_log(f"---------custom invoice update issue--------- {e}")

def createNotificationsForInvoice(sender, created, instance, *args, **kwargs):
    if created:
        created_by = instance.created_by if instance.created_by else "Customer(From Website)"
        title = f"Invoice Created (#{instance.number})"
        notification_info = " Generated Invoice for"
        created_by = instance.created_by
        createNotifications(title=title, notification_info=notification_info,
                            created_by=instance.created_by, created_who=instance.bill_to)
        

def UpdateProductOnExchange(sender, instance, created, **kwargs):
    try:
  
       instance.is_stock_updated_after_exchanged = False

       if  not created and str(instance.payment_status)=='3' and instance.is_regular and not instance.is_stock_updated_after_exchanged:
            print_log(f"Inside the signal if condition")
            print_log(f"exchanged_products {instance.exchange_products_json} TYPE {type(instance.exchange_products_json)} hello from update product on exchange")

            exchanged_products =instance.exchange_products_json['data']
            for item in exchanged_products:
                inv_product = Invoice_Products.objects.get(id=item)
                quantity = inv_product.quantity if type(inv_product.quantity) == int else int(inv_product.quantity)
                product = Products.objects.get(id=inv_product.product.id)
                product.stock += quantity
                product.save()
                variant = Variant.objects.get(id=inv_product.variant.id)
                variant.stock += quantity
                variant.save()
                inv_product.delete()
            instance.is_stock_updated_after_exchanged = True
            instance.save()
       if not created and instance.is_outlet and str(instance.payment_status)=='3' and not instance.is_stock_updated_after_exchanged:
            from inventory.models import OutLetProducts,OutletVariant
            outlet = instance.outlet
            exchanged_products =instance.exchange_products_json['data']
            for item in exchanged_products:
                try:
                    inv_product = Invoice_Products.objects.get(id=item)
                    product = OutLetProducts.objects.filter(outlet=outlet, product_id=inv_product.product.id,is_return=False).first()
                    print_log(f"outlet product {product}  invproduct {inv_product} quantity {inv_product.quantity}")
                    product.stock += inv_product.quantity
                    product.save()
                    variant = product.outletVariant.get(variant_id=inv_product.variant.id)
                    variant.stock += inv_product.quantity
                    variant.save()
                except Exception as e:
                    traceback.print_exc()
                    print_log(f"UpdateProductOutletOnReturn_issue {e}")

    except Exception as e:
        traceback.print_exc()
        print_log(f"UpdateProductOutletOnReturn_issue {e}")

def ConvertDraftToRegular(sender, instance, created, **kwargs):
    try:
        print(f"ConvertDraftToRegular = {created} is regular = {instance.is_regular} is convert to regular = {instance.is_convert_to_regular} is draft = {instance.is_draft}")
        if not created and instance.is_draft and instance.is_convert_to_regular:
            instance.is_regular = True
            instance.is_draft = False
            instance.is_convert_to_regular = False
            inv_prods = instance.invoice_products.all()
            for inv_prod in inv_prods:
                inv_prod.is_convert_to_regular = True
                inv_prod.save()
            instance.save()
    except Exception as e:
        traceback.print_exc()
        print_log(f"---------custom invoice update issue--------- {e}")








post_save.connect(ConvertDraftToRegular, sender=Invoice)
post_save.connect(createNotificationsForInvoice, sender=Invoice)
post_save.connect(SavePdfAndSendMail, sender=Invoice)
post_save.connect(createCustomer, sender=Invoice)
post_save.connect(UpdateProductOnReturn, sender=Invoice)
post_save.connect(UpdateProductOnExchange, sender=Invoice)
post_save.connect(ReduceVariantStock, sender=Invoice_Products)