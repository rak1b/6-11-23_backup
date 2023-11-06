from coreapp.base import BaseModel, BaseModelActive
from coreapp.helper import *
from utility.utils import slug_utils, model_utils,bar_image_utils
from utility.utils.notification_utils import *
from . import constants
from django.core.validators import MaxValueValidator
from django.utils.functional import cached_property
from promotions.models import Offer
from promotions.constants import OfferType
from django.db import models
from django.conf import settings
from django.db.models import Q
from django.db.models import Subquery, OuterRef
from datetime import date

class OutletVariant(BaseModel):
    variant = models.ForeignKey("inventory.Variant", on_delete=models.CASCADE)
    stock = models.IntegerField()
    outlet = models.ForeignKey("sales.Outlet", on_delete=models.CASCADE)
    is_return = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.variant.name}-ID{self.id}-{self.outlet.name}-{self.stock}"

class OutLetProducts(BaseModel):
    product = models.ForeignKey("inventory.Products", on_delete=models.CASCADE)
    stock = models.IntegerField()
    outletVariant = models.ManyToManyField(OutletVariant, blank=True)
    outlet = models.ForeignKey("sales.Outlet", on_delete=models.CASCADE)
    is_return = models.BooleanField(default=False)
    is_merged = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey("coreapp.User", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.SmallIntegerField(choices=constants.OutletProductReturnRequestStatus.choices, default=0)
    notes = models.TextField(null=True, blank=True)
    

    def __str__(self):
        return f"{self.product.name}-ID{self.id}-{self.outlet.name}-{self.stock}"


class Products(BaseModelActive):
    pid = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=200)
    main_category = models.SmallIntegerField(
        choices=constants.MainCategoryChoices.choices
    )
    category = models.ManyToManyField("inventory.Category")
    variant = models.ManyToManyField("inventory.Variant", blank=True)
    related_products = models.ManyToManyField(
        "inventory.Products", blank=True, related_name="related"
    )
    removed_products = models.ManyToManyField(
        "inventory.Products", blank=True, related_name="removed_related"
    )

    # sku = models.CharField(max_length=200)
    sku = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    stock = models.IntegerField()
    barcode = models.ImageField(upload_to="bar_codes/products/", blank=True)
    barcode_modified = models.ImageField(upload_to="bar_codes/products/", blank=True)
    qr_code = models.ImageField(upload_to="qr_codes/products/", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(
        null=True,
        blank=True,
    )
    thumb = models.ForeignKey(
        "coreapp.Document",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="thumb",
    )
    thumb2 = models.ForeignKey(
        "coreapp.Document",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="thumb2",
    )
    variant_chart = models.ForeignKey(
        "coreapp.Document",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="variant_chart",
    )
    thumb_resized = models.ImageField(
        upload_to="products/thumb_resized/", blank=True)
    feature_images = models.ManyToManyField(
        "coreapp.Document", related_name="feature_images", blank=True
    )
    minimum_quantity = models.IntegerField(default=00)
    tags = models.ManyToManyField("inventory.Tags", blank=True)
    is_trending = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_from_bulk = models.BooleanField(default=False)
    vendor_info = models.TextField(
        null=True,
        blank=True,
    )
    about_brand = models.TextField(
        null=True,
        blank=True,
    )
    shipping_info = models.TextField(
        null=True,
        blank=True,
    )
    variants_json = models.JSONField(
        null=True,
        blank=True,
    )
    order = models.IntegerField(default=0)
    is_show_website = models.BooleanField(default=True)
    is_update_related = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} - ID{self.id} - {self.stock}"
    
    def get_barcode_url(self):
        return f"{settings.MEDIA_HOST}/media/{self.barcode_modified}"

    def save(self, *args, **kwargs):
        try:
            model_utils.generate_product_barcode(self)
            bar_image_utils.Generate_barcode_modified(self)
            
            if not self.id:
                try:
                    ProductNotification(self.name)
                except Exception as e:
                    print_log(e)
            if not self.slug:
                self.slug = slug_utils.generate_unique_slug(self.name, self)


        except Exception as e:
            print_log("Error in saving product")
            print_log(str(e))
            pass
        return super(Products, self).save(*args, **kwargs)

    @cached_property
    def get_thumb_url(self):
        default_url = f"{settings.PLACEHOLDER_IMAGE}"
        return self.thumb.get_url if self.thumb else default_url

    @cached_property
    def get_thumb_url2(self):
        return self.thumb2.get_url if self.thumb2 else self.get_thumb_url

    @cached_property
    def get_resized_thumb_url(self):
        default_url = f"{settings.PLACEHOLDER_IMAGE}"
        return self.thumb.get_resized_url if self.thumb else default_url

    @cached_property
    def get_resized_thumb_url2(self):
        return (
            self.thumb2.get_resized_url if self.thumb2 else self.get_thumb_resized_url
        )

    @cached_property
    def get_variant_chart_url(self):
        return self.variant_chart.get_url if self.variant_chart else ""

    @property
    def get_related_products(self):
        return self.related_products.all()

    @property
    def get_related_products_in_depth(self):
        # Get directly related products
        direct_related = self.related_products.all()
        related_products = [self.id]

        for related in direct_related:
            related_products.append(related.id)
            related_products.extend(
                related.related_products.all().values_list("id", flat=True)
            )

        related_products = set(related_products)
        return Products.objects.filter(id__in=related_products)

    @property
    def get_removed_products(self):
        return self.removed_products.all()

    @property
    def get_related_product_variants(self):
        # variants =  self.related_products.values_list('variant', flat=True).distinct()
        # return [Variant.objects.get(id=variant) for variant in variants] if variants else []
        variant_ids = (
            self.related_products.filter(variant__is_active=True)
            .values_list("variant", flat=True)
            .distinct()
        )
        return Variant.objects.filter(id__in=variant_ids)

    @property
    def get_active_variants(self):
        return self.variant.filter(is_active=True)

    @property
    def get_all_variants(self):
        return self.get_related_product_variants | self.get_active_variants

    @cached_property
    def get_thumb_resized_url(self):
        default_url = f"{settings.PLACEHOLDER_IMAGE}"
        return self.thumb_resized.get_url if self.thumb_resized else default_url

    @property
    def get_category_name(self):
        names = ""
        for category in self.category.all():
            names += category.name + ", "
        return names[:-2]

    @property
    def get_feature_images(self):
        return (
            self.feature_images.all().order_by("order") if self.feature_images else []
        )


    @property
    def get_current_variant_images(self):
        return  self.get_active_variants.first().images.all()
    
    @property
    def get_related_variant_images(self):
        variant_images = []
        for variant in self.get_related_product_variants:
            variant_images.extend(variant.images.all())
        return variant_images

    @property
    def get_feature_images_web(self):
        related_products = self.related_products.all()
        distinct_feature_images = []
        distinct_feature_images.extend(self.feature_images.all().order_by("order"))
        if len(distinct_feature_images) < 1 and not self.main_category == 1:
            distinct_feature_images = self.get_active_variants.first().images.all()

        return distinct_feature_images
    @property
    def get_related_feature_images_web(self):
        related_products = self.related_products.all()
        distinct_feature_images = []
        for related_product in related_products:
            feature_images = related_product.feature_images.all().order_by("order")
            distinct_feature_images.extend(feature_images)
        if len(distinct_feature_images) < 1 and not self.main_category == 1:
            distinct_feature_images = self.get_related_variant_images
        return distinct_feature_images

    def get_product_offer(self):
        from django.utils import timezone
        current_datetime = timezone.now()
        offers = Offer.objects.filter(is_active=True, start_date__lte=current_datetime, expiry_date__gte=current_datetime).filter( Q(product=self) | Q(category__in=self.category.all()))
        return offers.first()

    def get_discount(self):
        offer = self.get_product_offer()
        if offer:
            return offer.discount_value
        else:
            return 0

    def get_offer_price(self):
        import math

        offer = self.get_product_offer()
        if offer:
            discount_type = offer.discount_type
            discount_value = offer.discount_value
            if discount_type == OfferType.PERCENTAGE:
                offer_price = math.ceil(
                    self.price - (self.price * discount_value / 100)
                )
            else:
                offer_price = math.ceil(self.price - discount_value)
        else:
            offer_price = math.ceil(self.price)
        return f"{offer_price:.1f}"

    def get_discount_type(self):
        offer = self.get_product_offer()
        if offer:
            return offer.discount_type

    def get_discount_type_text(self):
        offer = self.get_product_offer()
        if offer:
            return "%" if offer.discount_type == OfferType.PERCENTAGE else "৳"
        else:
            return "%"

    def today_total_amount(self):
        from sales.models import Invoice_Products
        import datetime

        today = datetime.datetime.today()

        start_date = datetime.datetime(
            year=today.year,
            month=today.month,
            day=today.day,
            hour=0,
            minute=0,
            second=0,
        )  # represents 00:00:00
        end_date = datetime.datetime(
            year=today.year,
            month=today.month,
            day=today.day,
            hour=23,
            minute=59,
            second=59,
        )
        todays_invoices_productss = Invoice_Products.objects.filter(
            invoice_date__range=(start_date, end_date)
        ).filter(product_id=self.id)
        total = 0
        for i in todays_invoices_productss:
            total += i.total
        return total

    def today_total_sales(self, product_id=None):
        from sales.models import Invoice_Products
        import datetime

        today = datetime.datetime.today()

        start_date = datetime.datetime(
            year=today.year,
            month=today.month,
            day=today.day,
            hour=0,
            minute=0,
            second=0,
        )  # represents 00:00:00
        end_date = datetime.datetime(
            year=today.year,
            month=today.month,
            day=today.day,
            hour=23,
            minute=59,
            second=59,
        )

        todays_invoices_productss = Invoice_Products.objects.filter(
            invoice__invoice_date__range=(start_date, end_date)
        )
        todays_invoices_productss = todays_invoices_productss.filter(
            product_id=self.id)

        total = 0
        for i in todays_invoices_productss:
            total += i.quantity
        return total


class Variant(BaseModelActive):
    attribute_value = models.ManyToManyField(
        "inventory.AttributeValue", blank=True)
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    stock = models.IntegerField()
    images = models.ManyToManyField("coreapp.Document", blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} - ID{self.id} stock - {self.stock}"

    @property
    def get_product(self):
        product = Products.objects.filter(variant=self).first()
        return product if product else {"id": None, "slug": None}

    @property
    def get_thumb_url(self):
        default_url = f"{settings.PLACEHOLDER_IMAGE}"
        first_image = self.images.first()
        return first_image.get_url if first_image else default_url
class AttributeValue(BaseModel):
    attribute = models.ForeignKey(
        "inventory.Attributes", on_delete=models.CASCADE, related_name="at_values"
    )
    value = models.CharField(max_length=200)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.attribute.name} - {self.value} - {self.id}"


class Attributes(BaseModel):
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ("-created_at",)

    def get_values(self):
        return AttributeValue.objects.filter(attribute=self)

    def __str__(self):
        return self.name


class Tags(BaseModel):
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class Category(BaseModelActive):
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="pt_category",
        null=True,
        blank=True,
    )
    slug = models.SlugField(max_length=250, null=True, blank=True)
    level = models.PositiveIntegerField(
        default=3, validators=[MaxValueValidator(5)])
    main_category = models.SmallIntegerField(
        choices=constants.MainCategoryChoices.choices
    )
    sub_main_category = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="sub_main_category_new",
        null=True,
        blank=True,
    )
    category_type = models.SmallIntegerField(
        choices=constants.CategoryType.choices)
    """
    Level 1 = Main Category - Home decor, In style
    Level 2 = home decor - For dining,for living
              In style -  Casual Wears,Party Wears,Exclusive Wears,Footwears,For Couples,Kids Zones
    Level 3 = For dining - Dining table, Dining chair
              For living - Sofa, Sofa cum bed
              Casual Wears - T-shirts, Shirts
              e.t.c
    """
    name = models.CharField(max_length=100, unique=True)
    thumb = models.ForeignKey(
        "coreapp.Document", on_delete=models.CASCADE, null=True, blank=True
    )
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=9999)

    class Meta:
        ordering = ("order","-created_at")

    def __str__(self):
        return self.name + " - Level : " + str(self.level)

    @property
    def has_categories(self):
        cats = Category.objects.filter(sub_main_category=self.id).first()
        return True if cats is not None else False

    @property
    def other_categories(self):
        cats = Category.objects.filter(
            sub_main_category=self.id).exclude(id=self.id)
        return cats if cats else []

    def count_products(self):
        return Products.objects.filter(category=self).count()

    def get_thumb_url(self):
        default_url = f"{settings.PLACEHOLDER_IMAGE}"
        return self.thumb.get_url if self.thumb else default_url

    def get_string_tree(self):
        category_tree = ""

        parent = self.parent
        while parent:
            if category_tree:
                category_tree = parent.name + " > " + category_tree
            else:
                category_tree = parent.name
            parent = parent.parent

        return category_tree

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_utils.generate_unique_slug(self.name, self)

        return super(Category, self).save(*args, **kwargs)


class Customer(BaseModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    mobile = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    # total_purchase = models.CharField(max_length=200)
    status = models.BooleanField(default=True)
    to_address = models.CharField(max_length=350)
    to_address2 = models.CharField(max_length=350, blank=True, null=True)
    to_zip_code = models.CharField(max_length=50, blank=True, null=True)
    to_city = models.CharField(max_length=50, blank=True, null=True)
    to_division = models.CharField(max_length=50, blank=True, null=True)
    to_district = models.CharField(max_length=50, blank=True, null=True)
    to_country = models.CharField(max_length=50, blank=True, null=True)
    redex_division = models.ForeignKey("utility.RedexDivision", on_delete=models.SET_NULL, blank=True, null=True)
    redex_district = models.ForeignKey("utility.RedexDistrict", on_delete=models.SET_NULL, blank=True, null=True)
    redex_area = models.ForeignKey("utility.RedexArea", on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_utils.generate_unique_slug(self.name, self)
        try:
            if self.id == None:
                CustomerNotifications_OnCreate(self.name)

            else:
                CustomerNotifications_OnUpdate(self.name)

        except Exception as e:
            print_log("Customer Notification Error" + str(e))

        return super(Customer, self).save(*args, **kwargs)

    @property
    def get_products_text(self):
        from sales.models import Invoice

        invoices = Invoice.objects.filter(to_mobile=self.mobile)
        inv_products = []
        for i in invoices:
            for inv_prod in i.invoice_products.all():
                inv_products.append(inv_prod)

        products_text = ""
        for inv in inv_products:
            name = inv.product.name if inv.product else inv.product_name
            name = f"{name} - {inv.variant_name}"
            products_text += f"{name} - {inv.quantity} - {inv.total} \n"
        return products_text

    @property
    def total(self):
        from sales.models import Invoice

        todays_invoices = Invoice.objects.filter(to_mobile=self.mobile)
        total = 0
        for i in todays_invoices:
            total += i.total_amount
        return total

    @property
    def total_purchase_method(self):
        from sales.models import Invoice

        total_amount = Invoice.objects.filter(to_mobile=self.mobile).aggregate(
            models.Sum("total_amount")
        )
        return (
            total_amount["total_amount__sum"]
            if total_amount["total_amount__sum"] is not None
            else 0
        )

    @property
    def invoice_count_method(self):
        from sales.models import Invoice

        total_amount = Invoice.objects.filter(to_mobile=self.mobile).count()
        return total_amount

    @property
    def get_invoice_numbers(self):
        from sales.models import Invoice

        invoices = Invoice.objects.filter(to_mobile=self.mobile)
        invoice_numbers = ""
        for invoice in invoices:
            invoice_numbers += f"{invoice.number}, "
        return invoice_numbers[:-2]

    def total_purchase(self, customer_phone=None, filter_by="all"):
        from sales.models import Invoice
        import datetime

        if filter_by == "all":
            todays_invoices = Invoice.objects.filter(to_mobile=customer_phone)
            total = 0
            for i in todays_invoices:
                total += i.total_amount
            return total

        if filter_by == "today":
            today = datetime.datetime.today()

            start_date = datetime.datetime(
                year=today.year,
                month=today.month,
                day=today.day,
                hour=0,
                minute=0,
                second=0,
            )  # represents 00:00:00
            end_date = datetime.datetime(
                year=today.year,
                month=today.month,
                day=today.day,
                hour=23,
                minute=59,
                second=59,
            )

            todays_invoices = Invoice.objects.filter(
                Q(invoice_date__range=(start_date, end_date))
                & Q(to_mobile=customer_phone)
            )
            total = 0
            for i in todays_invoices:
                total += i.total_amount
            return total

        if filter_by == "week":
            today = datetime.date.today()
            from utility.utils.filter_utils import getNumberofDays

            start_number = getNumberofDays()
            weeek_started = today - datetime.timedelta(days=start_number)
            todays_data = today + datetime.timedelta(
                days=1
            )  # so that it includes in the result

            invoices = Invoice.objects.filter(
                Q(invoice_date__range=(weeek_started, todays_data))
                & Q(to_mobile=customer_phone)
            )
            total = 0
            for i in invoices:
                total += i.total_amount
            return total

        if filter_by == "month":
            year = datetime.datetime.today().year
            month = datetime.date.today().month

            invoices = Invoice.objects.filter(
                invoice_date__year__gte=year,
                invoice_date__month__gte=month,
                invoice_date__year__lte=year,
                invoice_date__month__lte=month,
            )

            invoices = invoices.filter(Q(to_mobile=customer_phone))
            total = 0
            for i in invoices:
                total += i.total_amount
            return total

    def invoice_count(self, customer_phone=None, filter_by="all"):
        from sales.models import Invoice
        import datetime
        from utility.utils.filter_utils import getNumberofDays

        if filter_by == "all":
            return Invoice.objects.filter(to_mobile=customer_phone).count()

        if filter_by == "today":
            from sales.models import Invoice
            import datetime

            today = datetime.datetime.today()

            start_date = datetime.datetime(
                year=today.year,
                month=today.month,
                day=today.day,
                hour=0,
                minute=0,
                second=0,
            )  # represents 00:00:00
            end_date = datetime.datetime(
                year=today.year,
                month=today.month,
                day=today.day,
                hour=23,
                minute=59,
                second=59,
            )

            invoices_count = Invoice.objects.filter(
                Q(invoice_date__range=(start_date, end_date))
                & Q(to_mobile=customer_phone)
            ).count()

            return invoices_count

        if filter_by == "week":
            today = datetime.date.today()
            start_number = getNumberofDays()
            weeek_started = today - datetime.timedelta(days=start_number)
            todays_data = today + datetime.timedelta(
                days=1
            )  # so that it includes in the result

            invoices_count = Invoice.objects.filter(
                Q(invoice_date__range=(weeek_started, todays_data))
                & Q(to_mobile=customer_phone)
            ).count()

            return invoices_count

        if filter_by == "month":
            year = datetime.date.today().year
            month = datetime.date.today().month

            invoices_count = Invoice.objects.filter(
                Q(
                    invoice_date__year__gte=year,
                    invoice_date__month__gte=month,
                    invoice_date__year__lte=year,
                    invoice_date__month__lte=month,
                )
                & Q(to_mobile=customer_phone)
            ).count()

            return invoices_count

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name
