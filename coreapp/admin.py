from django.contrib.auth.admin import UserAdmin
from .models import User
from django.contrib import admin
from django.apps import apps
from import_export.admin import ImportExportMixin,ExportActionMixin
from import_export import resources
from import_export.fields import Field
from inventory.models import *
from sales.models import *
from import_export.formats import base_formats
import datetime
models = apps.get_models()


class CustomUserAdmin(UserAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = User
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'phone', 'name', 'type', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser',
         'groups', 'user_permissions',)}),  # 'is_customer' , 'is_seller'
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'name', 'type', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


for model in models:
    if not admin.site.is_registered(model) and model.__name__ not in ["Products","Invoice","Customer","DailyReport"]:
        admin.site.register(model)



def is_none( value):
    if value is None or value == '':
        return True
    return False

class ProductResource(resources.ModelResource):
    id = Field()
    name = Field()
    category = Field()
    is_active = Field()
    class Meta:
        model = Products
        fields = ('id', 'name', 'price', 'quantity','category',"sku","slug","stock","barcode","barcode_text",'description', 'thumb',"variants_json", 'created_at', 'updated_at')
        batch_size = None 
        formats = [base_formats.XLSX] # use xlsx format

    def __init__(self, start_date=None, end_date=None,filter=None,query=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.filter = filter
        self.query = query



    def get_queryset(self):
        queryset = super().get_queryset()
        if not is_none(self.start_date) and not is_none(self.end_date):
            start_date = datetime.datetime.strptime(self.start_date, '%m/%d/%Y').date()
            end_date = datetime.datetime.strptime(self.end_date, '%m/%d/%Y').date()
            queryset =  Products.objects.filter(updated_at__range=[start_date, end_date])
        elif not is_none(self.filter)  and  is_none(self.start_date) and  is_none(self.end_date):
            if self.filter  == 'today':
                queryset = filter_utils.todays_queryset(Products)
            elif self.filter  == 'week':
                queryset = filter_utils.weekly_queryset(Products)
            elif self.filter  == 'month':
                queryset = filter_utils.monthly_queryset(Products)
            elif self.filter  == 'year':
                queryset = filter_utils.yearly_queryset(Products)
            elif self.filter  == 'all':
                queryset = Products.objects.all().order_by('-created_at')
        elif  is_none(self.filter)  and  is_none(self.start_date) and  is_none(self.end_date):
            queryset = Products.objects.filter( Q(category__name__icontains=self.query) | Q(name__icontains=self.query) | Q(sku__icontains=self.query))
        else: 
            queryset = Products.objects.all().order_by('-created_at')
        return queryset

        
    def dehydrate_category(self, obj):
        return obj.get_category_name

    def dehydrate_id(self, obj):
        return obj.id
    def dehydrate_name(self, obj):
        return obj.name
    def dehydrate_is_active(self, obj):
        return "True" if obj.is_active else "False"
    

class CustomerResource(resources.ModelResource):
    id = Field()
    name = Field()
    total_purchase = Field()
    invoice_number = Field()
    products = Field()
#   to_address = models.CharField(max_length=350)
#     to_address2 = models.CharField(max_length=350, blank=True, null=True)
#     to_zip_code = models.CharField(max_length=50, blank=True, null=True)
#     to_city = models.CharField(max_length=50, blank=True, null=True)
#     to_division = models.CharField(max_length=50, blank=True, null=True)
#     to_district = models.CharField(max_length=50, blank=True, null=True)
#     to_country = models.CharField(max_length=50, blank=True, null=True)
    class Meta:
        model = Customer
        fields = ('id', 'name','total_purchase','invoice_count', 'email', 'mobile','slug','to_address','to_address2', 'to_zip_code','to_city','to_division','to_district','to_country', 'created_at', 'updated_at')
        batch_size = None 
        formats = [base_formats.XLSX] # use xlsx format

    def dehydrate_id(self, obj):
        return obj.id
    def dehydrate_name(self, obj):
        return obj.name
    def dehydrate_total_purchase(self, obj):
        return obj.total
    def dehydrate_invoice_number(self, obj):
        return obj.get_invoice_numbers
    def dehydrate_products(self, obj):
        return obj.get_products_text

    
    def __init__(self, filter=None,query=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter = filter
        self.query = query


        
    def get_queryset(self):
        queryset = super().get_queryset()
        if not is_none(self.filter)  :
            if self.filter  == 'today':
                queryset = filter_utils.todays_queryset(Customer)
            elif self.filter  == 'week':
                queryset = filter_utils.weekly_queryset(Customer)
            elif self.filter  == 'month':
                queryset = filter_utils.monthly_queryset(Customer)
            elif self.filter  == 'year':
                queryset = filter_utils.yearly_queryset(Customer)
            elif self.filter  == 'all':
                queryset = Customer.objects.all().order_by('-created_at')
            elif self.filter  == 'ascending':
                return  sorted(Customer.objects.all(), key= lambda current:current.total_purchase_method,reverse=False)
            elif self.filter  == 'descending':
                return  sorted(Customer.objects.all(), key= lambda current:current.total_purchase_method,reverse=True)
            else:
                queryset = Customer.objects.none()

        elif not is_none(self.query):
            queryset = Customer.objects.filter( Q(name__icontains=self.query) | Q(email__icontains=self.query) | Q(mobile__icontains=self.query))
        else: 
            queryset = Customer.objects.all().order_by('-created_at')
        return queryset
class DailyReportResource(resources.ModelResource):
    id = Field()
    is_custom = Field()
    sku = Field()

    def __init__(self, start_date=None, end_date=None,is_custom=None,query=None,outlet=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.is_custom = is_custom
        self.query = query
        self.outlet = outlet

    def dehydrate_id(self, obj):
        return obj.id
    def dehydrate_products(self, obj):
        if obj.products:
            return obj.products.name
        else:
            return obj.product_name
    def dehydrate_is_custom(self, obj):
        return "True" if obj.is_custom else "False"
    def dehydrate_sku(self, obj):
        if obj.products:
            return obj.products.sku
        else:
            return ""
    

    class Meta:
        model = DailyReport
        fields = ('id', 'products','quantity','total_amount', 'is_custom','created_at', 'updated_at')
        batch_size = None 
        formats = [base_formats.XLSX] # use xlsx format
    
    def get_queryset(self):
        queryset = super().get_queryset()
        print(f"self.is_custom: {self.is_custom} query: {self.query} start_date: {self.start_date} end_date: {self.end_date}")

        if self.is_custom is not None or self.outlet is not None:
            if str(self.is_custom) == "1":
                is_custom_queryset = DailyReport.objects.filter(is_custom=True)
            elif str(self.is_custom) == "0":
                is_custom_queryset = DailyReport.objects.filter(is_custom=False)
            else:
                is_custom_queryset = DailyReport.objects.all().order_by('-created_at')

            print(f"is_custom_queryset: {is_custom_queryset.count()}")

            if self.start_date and self.end_date:
                queryset = is_custom_queryset.filter(created_at__range=[self.start_date, self.end_date])
            elif not self.start_date and not self.end_date and self.query:
                print("query", self.query)
                queryset = is_custom_queryset.filter(Q(products__name__icontains=self.query) | Q(product_name__icontains=self.query))
            print(f"start date: {self.start_date} end date: {self.end_date}")
            print("queryset after ", queryset.count())
            queryset_test =   queryset.filter(id=1877)
            print("queryset_test ", queryset_test)
            if self.outlet is not None:
                queryset = queryset.filter(outlet__id=self.outlet)
            print("queryset after outlet ", queryset.count(), self.outlet)
        else:
            queryset = DailyReport.objects.all().order_by('-created_at')

        return queryset
class ProductAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = ProductResource
    list_display = ('name', 'stock', 'main_category', 'price')  # Customize as needed

    # Override the get_queryset method to use select_related and prefetch_related
    def get_queryset(self, request):
        # Define which fields to prefetch
        prefetch_related_fields = ('category', 'related_products', 'removed_products', 'variant')

        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related(*prefetch_related_fields)

        return queryset

class CustomerAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = CustomerResource
class DailyReportAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = DailyReportResource

admin.site.register(Products, ProductAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(DailyReport, DailyReportAdmin)


# class ProductAdmin(ImportExportMixin, admin.ModelAdmin):
#     list_display = ['name', 'category', 'quantity', 'sku','stock','price','discount','description','thumb','created_at','updated_at']
#     search_fields = ['name','description']
# admin.site.register(Products, ProductAdmin)