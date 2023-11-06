
from django.db import models
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
# Create your models here.
import random
from django.db.models import Q

from coreapp.base import BaseModel
from inventory.models import Variant, Products
from . import constants
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from rest_framework.decorators import action

from utility.utils import filter_utils,model_utils,slug_utils
import string
import json
from django.db.models.signals import pre_save, post_save

def get_random_string(length):
    letters = string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    return int(result_str)

class Chalan(BaseModel):
    number = models.CharField(max_length=50, blank=True, unique=True)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/invoice/', blank=True)
    outlet = models.ForeignKey("sales.Outlet", on_delete=models.SET_NULL, blank=True, null=True)
    chalan_outlet_products= models.ManyToManyField("inventory.OutLetProducts", blank=True,related_name="chalan_outlet_products")
    sub_total = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)
    total_due = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)
    total_paid = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)
    total_amount = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)
    total_discount = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)
    created_by = models.ForeignKey("coreapp.user", on_delete=models.SET_NULL, blank=True, null=True, related_name="chalan_created_by")
    last_modified_by  = models.ForeignKey("coreapp.user", on_delete=models.SET_NULL, blank=True, null=True, related_name="chalan_last_modified_by")
    is_chalan_outlet_products_set = models.BooleanField(default=False) 
    is_merged = models.BooleanField(default=False)
    def __str__(self):
        return str(self.number)
    
    def save(self, *args, **kwargs):
        if not self.number:
            self.number = model_utils.get_invoice_code(Chalan,prefix="CHL")
        if not self.slug:
            self.slug = self.number
            # self.slug = slug_utils.generate_unique_slug(self.number,self)
        if not self.id:
            model_utils.generate_qrcode(self,self.number)
        return super(Chalan, self).save(*args, **kwargs)
    
    @property
    def get_chalan_products(self):
        return Products.objects.filter(id__in=self.chalan_outlet_products.all().values_list("product",flat=True))

    @property
    def get_products_count(self):
        from django.db.models import Sum
        return self.chalan_outlet_products.all().aggregate(Sum("stock"))["stock__sum"] if self.chalan_outlet_products.all().aggregate(Sum("stock"))["stock__sum"] else 0


class Invoice_Products(BaseModel):
    product = models.ForeignKey("inventory.Products", blank=True, null=True, on_delete=models.SET_NULL)
    variant = models.ForeignKey("inventory.Variant", blank=True, null=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=0)
    total = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)
    product_name = models.CharField(max_length=100, blank=True, null=True)
    variant_name = models.CharField(max_length=100, blank=True, null=True)
    is_custom = models.BooleanField(default=False)
    is_purchase_order = models.BooleanField(default=False)
    is_requisition_order = models.BooleanField(default=False)
    is_outlet = models.BooleanField(default=False)
    is_regular = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    is_convert_to_regular = models.BooleanField(default=False)
    outlet = models.ForeignKey("sales.Outlet", on_delete=models.SET_NULL, blank=True, null=True)
    invoice_date = models.DateField()
    def __init__(self, *args, **kwargs):
        super(Invoice_Products, self).__init__(*args, **kwargs)
        self.prev_quantity = self.quantity

    @property
    def get_in_stock(self):
        return True if self.variant.stock >= self.quantity else False

    class Meta:
        ordering = ('-invoice_date',)

    def __str__(self):
        return f"{self.product_name} - ID: {self.id}"
        
        
class Invoice(BaseModel):
    outlet = models.ForeignKey("sales.Outlet", on_delete=models.SET_NULL, blank=True, null=True)
    checkout = models.ForeignKey("order.Checkout", on_delete=models.SET_NULL, blank=True, null=True)
    number = models.CharField(max_length=50, blank=True, unique=True)
    invoice_products = models.ManyToManyField(Invoice_Products, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/invoice/', blank=True)
    qr_code_text = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    source = models.SmallIntegerField(choices=constants.SourceChoices.choices,default=1)
    invoice_date = models.DateField()
    reference_id = models.CharField(max_length=50, blank=True, null=True)
    bill_from = models.CharField(max_length=50,default="KAARUJ")
    bill_to = models.CharField(max_length=50,blank=True,null=True)
    from_mobile = models.CharField(max_length=50,default='+8801980907892')
    to_mobile = models.CharField(max_length=50)
    from_email = models.CharField(max_length=150,default="kaarujbangladesh@gmail.com")
    to_email = models.CharField(max_length=150, blank=True, null=True)
    from_address = models.CharField(max_length=350,default="Road: 42, Gulshan 2, Dhaka, Bangladesh")
    to_address = models.CharField(max_length=350,blank=True,null=True)
    to_address2 = models.CharField(max_length=350, blank=True, null=True)
    to_zip_code = models.CharField(max_length=50, blank=True, null=True)
    to_city = models.CharField(max_length=50, blank=True, null=True)
    to_division = models.CharField(max_length=50, blank=True, null=True)
    to_district = models.CharField(max_length=50, blank=True, null=True)

    redex_division = models.ForeignKey("utility.RedexDivision", on_delete=models.SET_NULL, blank=True, null=True)
    redex_district = models.ForeignKey("utility.RedexDistrict", on_delete=models.SET_NULL, blank=True, null=True)
    redex_area = models.ForeignKey("utility.RedexArea", on_delete=models.SET_NULL, blank=True, null=True)

    to_country = models.CharField(max_length=50, blank=True, null=True)
    delivery_type = models.SmallIntegerField(choices=constants.DeliveryTypeChoices.choices)
    delivery_charge = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)
    delivery_charge_type = models.SmallIntegerField(choices=constants.deliveryChargeChoices.choices)
    payment_type = models.SmallIntegerField(choices=constants.PaymentTypeChoices.choices)
    mixed_payment_details = models.JSONField(blank=True, null=True)
    discount_type = models.SmallIntegerField(choices=constants.DiscountChoices.choices)
    delivery_status = models.SmallIntegerField(choices=constants.DeliveryStatusChoices.choices)
    sub_total = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)
    total_due = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)
    total_paid = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)
    total_amount = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)
    total_discount = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)
    payment_status = models.SmallIntegerField(choices=constants.InvoiceChoices.choices)
    notes = models.TextField(blank=True, null=True)
    notes2 = models.TextField(blank=True, null=True)
    exchange_products_json = models.JSONField(blank=True, null=True)
    product_list_json = models.JSONField(blank=True, null=True)
    invoice_view_json = models.JSONField(blank=True, null=True)
    created_for = models.ForeignKey("coreapp.user", on_delete=models.SET_NULL, blank=True, null=True, related_name="invoice_created_for")
    created_by = models.ForeignKey("coreapp.user", on_delete=models.SET_NULL, blank=True, null=True, related_name="invoice_created_by")
    send_pdf = models.BooleanField()
    send_pdf_admin = models.BooleanField(default=False)
    card_holder_name = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    banK_account_number = models.CharField(max_length=100, blank=True, null=True)
    banK_account_name = models.CharField(max_length=100, blank=True, null=True)
    banK_branch_name = models.CharField(max_length=100, blank=True, null=True)
    bkash_number = models.CharField(max_length=11, blank=True, null=True)
    bkash_trx_number = models.CharField(max_length=11, blank=True, null=True)  
    nagad_number = models.CharField(max_length=11, blank=True, null=True)
    nagad_trx_number = models.CharField(max_length=11, blank=True, null=True)
    last_modified_by  = models.ForeignKey("coreapp.user", on_delete=models.SET_NULL, blank=True, null=True, related_name="invoice_last_modified_by")
    is_regular = models.BooleanField(default=False)
    is_custom = models.BooleanField(default=False)
    is_purchase_order = models.BooleanField(default=False)
    is_requisition_order = models.BooleanField(default=False)
    is_stock_updated_after_return = models.BooleanField(default=False)
    is_outlet = models.BooleanField(default=False)
    is_stock_updated_after_exchanged = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    is_convert_to_regular = models.BooleanField(default=False)
    ssl_status = models.CharField(max_length=255, blank=True, null=True)
    total_cash_recieved = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)
    change_amount = models.DecimalField(default=00.00, decimal_places=2, max_digits=10)

    class Meta:
        ordering = ('-invoice_date',"-created_at")

    def __str__(self):
        return str(self.to_email)

    def delete(self, *args, **kwargs):
        self.invoice_products.all().delete()
        super().delete(*args, **kwargs)
    @property
    def total_amount_with_discount(self):
        import math
        if (self.discount_type == 0):

            return int(self.total_amount) - int(self.total_discount)
        else:
            return int(self.total_amount) - (int(self.total_amount) * (int(self.total_discount) / 100))

    def get_invoice_products(self):
        return self.invoice_products.all()
    

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = model_utils.get_invoice_code(Invoice,prefix="INV")
        if not self.slug:
            self.slug = self.number
            # self.slug = slug_utils.generate_unique_slug(self.number,self)
        if not self.id:
            model_utils.generate_qrcode(self,self.number)
            from utility.utils import notification_utils
            notification_utils.update_dashboard_notification("invoice",1,True)
        return super(Invoice, self).save(*args, **kwargs)



class DailyReport(models.Model):
    products = models.ForeignKey(Products, on_delete=models.CASCADE,blank=True,null=True)
    quantity = models.IntegerField()
    total_amount = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100, blank=True, null=True)
    is_custom = models.BooleanField(default=False)
    is_purchase_order = models.BooleanField(default=False)
    is_requisition_order = models.BooleanField(default=False)
    is_outlet = models.BooleanField(default=False)
    is_regular = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    outlet = models.ForeignKey("sales.Outlet", on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.product_name} - {self.created_at.strftime('%d/%m/%Y')}"




class Outlet(BaseModel):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=100)
    email = models.EmailField(max_length=100,default="",blank=True,null=True)
    thumb = models.ForeignKey("coreapp.Document", on_delete=models.SET_NULL, blank=True, null=True)
    location = models.TextField(blank=True, null=True,default="Dhaka,Bangladesh")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.id}"

    def get_thumb_url(self):
        return self.thumb.get_url if self.thumb else self.get_default()
    
    def get_products(self,query):
        from inventory.models import OutLetProducts
        products = OutLetProducts.objects.filter(outlet=self,is_return=False).values_list("product", flat=True)
        return Products.objects.filter(id__in=products).filter(Q(name__icontains=query) | Q(sku__icontains=query) )
    
