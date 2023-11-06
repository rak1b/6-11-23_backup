from ...models import *
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from utility.api.admin.serializers import *


class InvoiceProductSerializer(ModelSerializer):
    thumb = serializers.ReadOnlyField(source='variant.get_thumb_url')
    sku = serializers.ReadOnlyField(source='product.sku')
    in_stock = serializers.ReadOnlyField(source='get_in_stock')
    class Meta:
        model = Invoice_Products
        fields = '__all__'

class VariantSerializerInvoice(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields='__all__'

class InvoiceProductSerializerInvoice(serializers.ModelSerializer):
    variant_details = VariantSerializerInvoice(read_only=True,source= 'variant')
    product_thumb = serializers.ReadOnlyField(source='product.get_thumb_url')
    product_name = serializers.SerializerMethodField()
    product_price = serializers.ReadOnlyField(source='product.price')
    class Meta:
        model = Invoice_Products
        fields = ['id', 'variant', 'quantity', 'total','product_name','product_price','product_thumb','variant_details']
    def get_product_name(self, instance):
        return instance.product.name if instance.product else instance.product_name
    

class InvoiceListSerializer(serializers.ModelSerializer):
    prepared_by = serializers.ReadOnlyField(source='created_by.get_full_name')
    last_modified_by = serializers.SerializerMethodField()
    class Meta:
        model =  Invoice
        fields = ['id','slug','number','source','prepared_by','last_modified_by','is_custom','delivery_type','delivery_status','payment_status','payment_type','payment_status','total_amount','invoice_date','bill_to','to_mobile']
    def get_last_modified_by(self, instance):
        created_by = instance.created_by.get_full_name() if instance.created_by else None
        last_modified_by = instance.last_modified_by.get_full_name() if instance.last_modified_by else None
        return last_modified_by if last_modified_by else created_by
class InvoiceSerializer_AddressFilter(serializers.Serializer):
    invoice_id = serializers.CharField(max_length=255,required=False)
    invoice_number = serializers.CharField(max_length=255,required=False)
    product_name = serializers.CharField(max_length=255,required=False)
    product_id = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(required=False)
    total = serializers.FloatField(required=False)
    address = serializers.CharField(max_length=255,required=False)
    address2 = serializers.CharField(max_length=255,required=False)
    phone = serializers.CharField(max_length=255,required=False)
    email = serializers.CharField(max_length=255,required=False)
    name = serializers.CharField(max_length=255,required=False)
    invoice_date = serializers.DateField(required=False)
  
class InvoiceSerializer(ModelSerializer):
    invoice_products = InvoiceProductSerializer(many=True)
    invoice_products_formatted = serializers.SerializerMethodField()
    redex_division_details = RedexDivisionSerializerMinimal(read_only=True,source='redex_division')
    redex_district_details = RedexDistrictSerializerMinimal(read_only=True,source='redex_district')
    redex_area_details = RedexAreaSerializerMinimal(read_only=True,source='redex_area')
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['slug','number','qr_code','qr_code_text']

    def validate(self, attrs):
        instance = self.instance
        is_draft = attrs.get('is_draft',False)
        if instance is None :
            invoice_products = attrs.get('invoice_products')
            if len(invoice_products) == 0:
                raise serializers.ValidationError("Invoice must have at least one product,please check quantity.")
            for invoice_product in invoice_products:
                product_name = invoice_product.get('product_name')
                quantity = invoice_product.get('quantity')
                quantity = int(quantity) 
                if quantity <= 0:
                    raise serializers.ValidationError(f"{product_name}'s quantity  must be greater than 0")
        return super().validate(attrs)

    def create(self, validated_data):
        print_log(validated_data)
        invoice_products = validated_data.pop('invoice_products')
        invoice = Invoice.objects.create(**validated_data)
        try:
            invoice.created_by = self.context.get('request').user
            invoice.last_modified_by = self.context.get('request').user
        except:
            pass
        for invoice_product in invoice_products:
            created_invoice_product = Invoice_Products.objects.create(invoice=invoice, **invoice_product)
            invoice.invoice_products.add(created_invoice_product) 
        invoice.send_pdf_admin=True
        if invoice.source == 0:
            invoice.send_pdf=True
        invoice.save()
        return invoice

    def get_invoice_products_formatted(self, instance):       
        invoice_products = {}
        for invoice_product in instance.invoice_products.all().order_by('created_at'):
            product_name = invoice_product.product.name if invoice_product.product else invoice_product.product_name
            # product_name = f"{invoice_product.product.name} [[{invoice_product.product.sku}]]" if invoice_product.product else invoice_product.product_name
            if product_name not in invoice_products:
                invoice_products[product_name] = []
            invoice_product_data = InvoiceProductSerializerInvoice(invoice_product).data
            invoice_products[product_name].append(invoice_product_data)
        return invoice_products
     
class InvoiceSerializer_Update(ModelSerializer):
    invoice_products_details = serializers.ListField(child=serializers.DictField(),write_only=True)
    invoice_products = InvoiceProductSerializer(many=True,read_only=True)
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['slug','number','qr_code','qr_code_text']

    def validate(self, attrs):
        instance = self.instance
        is_convert_to_regular = attrs.get('is_convert_to_regular',False)
        print_log(f"instance {instance} is_draft {instance.is_draft} invoice_products {instance.invoice_products.all()} is_convert_to_regular {is_convert_to_regular}")
        if is_convert_to_regular:
            invoice_products = instance.invoice_products.all()
            for invoice_product in invoice_products:
                product_name = invoice_product.product.name if invoice_product.product else invoice_product.product_name
                variant_name = invoice_product.variant.name if invoice_product.variant else invoice_product.variant_name
                in_stock = invoice_product.get_in_stock
                if in_stock==False:
                    raise serializers.ValidationError({f"Low Stock":[f"{product_name}-{variant_name}"]})
        return super().validate(attrs)

    def update(self,instance, validated_data):
        request = self.context.get('request')
        invoice_products = validated_data.pop('invoice_products_details',[])
        for invoice_product in invoice_products:
            invoice_product_id = invoice_product.get('id')
            if invoice_product_id:
                inv_prod_instance =Invoice_Products.objects.get(id=invoice_product_id)
                serializer_inv_prod = InvoiceProductSerializer(data=invoice_product,instance=inv_prod_instance,partial=True)
                if serializer_inv_prod.is_valid():
                    serializer_inv_prod.save()
                
            else:
                try:
                    invoice_product['product'] = Products.objects.get(id=invoice_product.get('product'))
                    invoice_product['variant'] = Variant.objects.get(id=invoice_product.get('variant'))
                    invoice_product['outlet'] = Outlet.objects.get(id=invoice_product.get('outlet'))
                    created_invoice_product = Invoice_Products.objects.create( **invoice_product)
                    instance.invoice_products.add(created_invoice_product)
                except Exception as e:
                    print_log(f"Error in invoice update {e}")
                    raise serializers.ValidationError(f"Error in invoice update {e}")
                    
                
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.last_modified_by = request.user
        instance.save()
        return instance


class All_InvoiceSerializer(serializers.ModelSerializer):
    prepared_by = serializers.ReadOnlyField(source='created_by.get_full_name')
    last_modified_by = serializers.ReadOnlyField(source='last_modified_by.get_full_name')
    

    class Meta:
        model =  Invoice
        fields = "__all__"


