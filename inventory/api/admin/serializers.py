from inventory.models import *
from rest_framework import serializers
from ...models import *
from inventory.api.inventory.serializers import *
from sales.api.inventory.serializers import *


class OutletVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutletVariant
        exclude = ['created_at','updated_at','outlet']
class OutletVariantSerializerRetrieve(serializers.ModelSerializer):
    variant_details = VariantSerializer(source='variant',read_only=True)

    class Meta:
        model = OutletVariant
        exclude = ['created_at','updated_at']

class OutletVariantSerializerRetrieveInvoice(serializers.ModelSerializer):
    variant_details = VariantSerializerForOutletInvoice(source='variant',read_only=True)

    class Meta:
        model = OutletVariant
        exclude = ['created_at','updated_at']
class OutletProductSerializer(serializers.ModelSerializer):
    outletVariant = OutletVariantSerializer(many=True)
    outlet_name = serializers.ReadOnlyField(source='outlet.name')

    class Meta:
        model = OutLetProducts
        fields = '__all__'
        read_only_fields = ['created_at','updated_at','outletVariant']
    
    def update_variant_stock(self, id, stock_to_reduce):
        try:
            variant = Variant.objects.get(id=id)
            variant.stock += stock_to_reduce
            variant.save()
        except Exception as e:
            print_log(f"Error in outlet product creation {e}")
    
    def validate(self, data):
        instance = self.instance
        if instance is None:
            try:
                outlet = data['outlet']
                product = data['product']
            except Exception as e:
                raise serializers.ValidationError("Outlet and Product is required")
        else:
            outlet = data.get('outlet',instance.outlet)
            product = data.get('product',instance.product)
        outlet_products = OutLetProducts.objects.filter(outlet=outlet,product=product,is_return=True,status=0)
        if instance:
            outlet_products = outlet_products.exclude(id=instance.id)
        if outlet_products:
            raise serializers.ValidationError("Product already exists in this outlet")
       
        return data
    
    
    def create(self, validated_data):
        outletVariant = validated_data.pop('outletVariant')
        outlet = validated_data['outlet']
        product = validated_data['product']
        outlet_product = OutLetProducts.objects.create(**validated_data)
        outlet_variant_ids = []
        for variant in outletVariant:
            variant['outlet'] = outlet
            outlet_variant = OutletVariant.objects.create(**variant)
            outlet_variant_ids.append(outlet_variant.id)
            stock_to_reduce = -1 * outlet_variant.stock
            self.update_variant_stock(variant['variant'].id,stock_to_reduce)
        outlet_product.outletVariant.set(outlet_variant_ids)
        outlet_product.product.stock -= outlet_product.stock
        outlet_product.product.save()
        return outlet_product
    
    
    def update(self, instance, validated_data):
        outletVariant = validated_data.pop('outletVariant')
        # outlet_product = OutLetProducts.objects.update(**validated_data)
        product_stock = validated_data.get('stock')

        outlet_variant_ids = []
        for curr_variant in outletVariant:
            curr_variant['outlet'] = instance.outlet
            variant_id = curr_variant['variant'].id
            current_outlet_prod_variants = instance.outletVariant.all().filter(variant=variant_id).first()
            if  current_outlet_prod_variants:
                outlet_variant_id = current_outlet_prod_variants.id
                curr_variant['id'] = outlet_variant_id
                outlet_variant = OutletVariant.objects.get(id=outlet_variant_id,variant_id=variant_id)
                outlet_variant_prev_stock = outlet_variant.stock
                for key,value in curr_variant.items():
                    setattr(outlet_variant,key,value)
                outlet_variant.save()
                outlet_variant_after_stock = outlet_variant.stock

                stock_reduce_or_increase = outlet_variant_prev_stock - outlet_variant_after_stock
                self.update_variant_stock(variant_id,stock_reduce_or_increase)


            else:
                outlet_variant = OutletVariant.objects.create(**curr_variant)
                stock_to_reduce = -1 * outlet_variant.stock
                self.update_variant_stock(variant_id,stock_to_reduce)
            if type(outlet_variant) == OutletVariant:
                outlet_variant_ids.append(outlet_variant.id)
        instance.outletVariant.set(outlet_variant_ids)
        product_reduce_or_increase =  instance.stock - product_stock
        instance.product.stock += product_reduce_or_increase
        instance.product.save()
        super().update(instance,validated_data)
        return instance


class OutletProductSerializerForReturn(serializers.ModelSerializer):
    outletVariant = OutletVariantSerializer(many=True)
    outlet_name = serializers.ReadOnlyField(source='outlet.name')

    class Meta:
        model = OutLetProducts
        fields = '__all__'
        read_only_fields = ['created_at','updated_at','outletVariant']

    def validate(self, data):
        instance = self.instance
        print_log(f"validated_data1212 {data} instance {instance}")
        print_log(f"stock {data.get('stock')} instance {instance}")
        if instance is None:
            stock = data.get('stock',0)
            if stock < 1:
                raise serializers.ValidationError("Stock should be greater than 0")
            try:
                outlet = data['outlet']
                product = data['product']
            except Exception as e:
                raise serializers.ValidationError(f"Outlet and Product is required instance {instance} - {e}")
        else:
            outlet = data.get('outlet',instance.outlet)
            product = data.get('product',instance.product)
        outlet_products = OutLetProducts.objects.filter(outlet=outlet,product=product,is_return=True,status=0)
        if instance:
            outlet_products = outlet_products.exclude(id=instance.id)
        if outlet_products.exists():
            raise serializers.ValidationError("Product Stock request is already in progress")
        return data
    def update_variant_stock(self, id, stock_to_reduce):
        try:
            variant = Variant.objects.get(id=id)
            variant.stock += stock_to_reduce
            variant.save()
        except Exception as e:
            print_log(f"Error in outlet product creation {e}")
    
    def create(self, validated_data):
        outletVariant = validated_data.pop('outletVariant')
        outlet = validated_data['outlet']
        product = validated_data['product']
        validated_data['user'] = self.context['request'].user
        outlet_product = OutLetProducts.objects.create(**validated_data)
        outlet_variant_ids = []
        for variant in outletVariant:
            variant['outlet'] = outlet
            outlet_variant = OutletVariant.objects.create(**variant)
            outlet_variant_ids.append(outlet_variant.id)
        outlet_product.outletVariant.set(outlet_variant_ids)
        outlet_product.product.save()
        return outlet_product
    
    def update(self, instance, validated_data):
        status = validated_data.get('status')
        if status in [1,'1']:
            outlet_product = OutLetProducts.objects.filter(product=instance.product,outlet=instance.outlet,is_return=False).first()
            print_log(f"outlet_product {outlet_product} outlet_product.stock {outlet_product.stock} instance.stock {instance.stock} instance.outletVariant.all() {instance.outletVariant.all()}")

            if outlet_product:
                product_reduce = instance.stock
                outlet_product.stock -= product_reduce
                outlet_product.product.stock += product_reduce
                outlet_product.product.save()
                for outlet_variant in instance.outletVariant.all():
                    variant_id = outlet_variant.variant.id
                    outlet_product_variant = outlet_product.outletVariant.all().filter(variant_id=variant_id).first()
                    if outlet_product_variant:
                        outlet_product_variant.stock -= outlet_variant.stock
                        outlet_product_variant.variant.stock += outlet_variant.stock
                        outlet_product_variant.variant.save()
                        outlet_product_variant.save()
                    outlet_product.save()
                    
                    print(f"variant_id {variant_id} variant { outlet_variant.variant} " )




        super().update(instance,validated_data)
        return instance

class OutletProductSerializerForList(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product',read_only=True)
    outlet_name = serializers.ReadOnlyField(source='outlet.name')
    user_name = serializers.ReadOnlyField(source='user.name')
    class Meta:
        model = OutLetProducts
        fields = '__all__'
        read_only_fields = ['created_at','updated_at','outletVariant','outlet_name']

class OutletProductSerializerForRetrieve(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product',read_only=True)
    outletVariant = OutletVariantSerializerRetrieve(many=True)
    outlet_name = serializers.ReadOnlyField(source='outlet.name')
    user_name = serializers.ReadOnlyField(source='user.name')
    
    class Meta:
        model = OutLetProducts
        fields = '__all__'
        read_only_fields = ['created_at','updated_at','outletVariant']


class OutletProductSerializerForInvoice(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField()
    offer_price = serializers.ReadOnlyField(source='get_offer_price')
    thumb_url = serializers.ReadOnlyField(source='thumb.get_url')
    discount = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    thumb_url = serializers.SerializerMethodField()
    class Meta:
        model = Products
        fields = ['id','name',"created_at","updated_at",'description','thumb','sku','is_show_website','variants','offer_price','price','discount','stock','thumb_url',"barcode","slug"]
    
    def get_discount(self, obj):
        return 0
    def get_thumb_url(self, obj):
        return obj.get_thumb_url
    def get_outlet_product(self, obj):
        from inventory.models import OutletVariant
        outlet = self.context.get('outlet')
        outlet_product = OutLetProducts.objects.filter(outlet=outlet,product=obj,is_return=False)
        return  outlet_product if outlet_product else []
    
        
    def get_stock(self, obj):
        outlet_product = self.get_outlet_product(obj)
        stock = 0
        for product in outlet_product:
            stock += product.stock
        return stock
    
    def get_variants(self, obj):
        all_outlet_product = self.get_outlet_product(obj)
        variants_list = []
        for outlet_product in all_outlet_product:
            variants =  outlet_product.outletVariant.all().filter(is_return=False).values_list('variant',flat=True)
            print_log(f"variants {variants}") 
            variants_list.extend(variants)
        variants = Variant.objects.filter(id__in=variants_list)
        context = self.context
        return VariantSerializerForOutletInvoice(variants,many=True,context=context).data

class OutletProductSerializerForChalanRetrieve(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField()
    offer_price = serializers.ReadOnlyField(source='get_offer_price')
    thumb_url = serializers.ReadOnlyField(source='get_thumb_url')
    thumb_resized_url = serializers.ReadOnlyField(source='get_resized_thumb_url')
    discount = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    class Meta:
        model = Products
        fields = ['id','name','thumb','sku','is_show_website','variants','offer_price','price','discount','stock','thumb_url',"thumb_resized_url"]
    
    def get_discount(self, obj):
        return 0
    
    def get_outlet_product(self, obj):
        from inventory.models import OutletVariant
        outlet = self.context.get('outlet')
        outlet_product = OutLetProducts.objects.filter(outlet=outlet,product=obj,is_return=False).first()
        print_log(f"outlet_product from model {outlet_product}")
        return  outlet_product if outlet_product else None
    
        
    def get_stock(self, obj):
        outlet_product = self.get_outlet_product(obj)
        return outlet_product.stock if outlet_product else 0
    
    def get_variants(self, obj):
        outlet_product = self.get_outlet_product(obj)
        print(f"outlet_product {outlet_product} ")
        variants =  outlet_product.outletVariant.all().filter(is_return=False).values_list('variant',flat=True) if outlet_product else []
        variants = Variant.objects.filter(id__in=variants)
        context = self.context
        return VariantSerializerForOutletChalanRetrieve(variants,many=True,context=context).data
class ChalanProductSerializerInvoice(serializers.ModelSerializer):
    variant_details = VariantSerializerInvoice(read_only=True,source= 'outletVariant.variant')
    product_thumb = serializers.ReadOnlyField(source='product.get_thumb_url')
    product_name = serializers.SerializerMethodField()
    product_price = serializers.ReadOnlyField(source='product.price')
    class Meta:
        model = OutLetProducts
        fields = ['id', 'variant', 'quantity', 'total','product_name','product_price','product_thumb','variant_details']
    def get_product_name(self, instance):
        return instance.product.name 