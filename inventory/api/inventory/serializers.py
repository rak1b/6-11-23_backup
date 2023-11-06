from ...models import *
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from coreapp.api.serializers import DocumentSerializer
from utility.api.admin.serializers import *

class CategorySerializer(serializers.ModelSerializer):
    
    subcategories = serializers.SerializerMethodField()
    thumb_url = serializers.ReadOnlyField(source='get_thumb_url')
    # parent_name = serializers.ReadOnlyField(source='parent.name', allow_null=True)
    # tree = serializers.ReadOnlyField(source="category_tree_exclude_current")
    products = serializers.ReadOnlyField(source="count_products")
    tree = serializers.ReadOnlyField(source="get_string_tree")

    class Meta:
        model = Category
        # fields = ['id', 'name','level', 'subcategories']
        fields = '__all__'
        read_only_fields = ['slug',]

    def get_subcategories(self, obj):
        subcategories = Category.objects.filter(parent=obj)
        serializer = CategorySerializer(subcategories, many=True)
        return serializer.data
    
    # def create(self, validated_data):
    #     order = validated_data.get('order')
    #     category_type = validated_data.get('category_type',None)
    #     if category_type in [1,"1"]:
    #         catgories = Category.objects.filter(sub_main_category=None,order=order).first()
    #         if catgories is not None:
    #             raise serializers.ValidationError({'order': [f'Order {order} already exists in {catgories.name}.']})

            
    #     return super().create(validated_data)
    
    # def update(self,validated_data):
    #     instance = self.instance    
    #     order = validated_data.get('order')
    #     if order:
    #         category_type = instance.category_type
    #         if category_type in [1,"1"]:
    #             catgories = Category.objects.filter(sub_main_category=None,order=order).exclude(id=instance.id).first()
    #             if catgories is not None:
    #                 catgories.order = instance.order
    #                 catgories.save()

    #     return super().update(validated_data)
    


    

        
    
class AttributeValueSerializer(serializers.ModelSerializer):
    # attribute_details = AttributeSerializer(source='attribute', read_only=True)]
    class Meta:
        model = AttributeValue
        fields = '__all__'
    
class VariantSerializer(serializers.ModelSerializer):
    # attribute_value_details = AttributeValueSerializer(source='attribute_value', read_only=True,many=True)
    attribute_value = AttributeValueSerializer(many=True)
    images_details = DocumentSerializer(source='images', read_only=True,many=True)
    class Meta:
        model = Variant
        fields = '__all__'
    
class VariantSerializerForOutletInvoice(serializers.ModelSerializer):
    images_details = DocumentSerializer(source='images', read_only=True,many=True)
    stock = serializers.SerializerMethodField()
    class Meta:
        model = Variant
        fields = ['id','name','price','is_active','images_details','stock']
    
    def get_stock(self, obj):
        from inventory.models import OutletVariant
        outlet = self.context.get('outlet')
        outlet_variant = OutletVariant.objects.filter(outlet=outlet,variant=obj,is_return=False)
        stock = 0
        print(f"outlet_variant: {outlet_variant}")
        for variant in outlet_variant:
            stock += variant.stock            
        return stock    
class VariantSerializerForOutletChalanRetrieve(serializers.ModelSerializer):
    images_details = DocumentSerializer(source='images', read_only=True,many=True)
    stock = serializers.SerializerMethodField()
    class Meta:
        model = Variant
        fields = ['id','name','price','is_active','images_details','stock']
    
    def get_stock(self, obj):
        from inventory.models import OutletVariant
        outlet = self.context.get('outlet')
        outlet_variant = OutletVariant.objects.filter(outlet=outlet,variant=obj,is_return=False).first()
        print(f"outlet_variant {outlet_variant} {outlet} {obj}")
        return outlet_variant.stock if outlet_variant else 0

    

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'

class CategorySerializerForProducts(ModelSerializer):
    class Meta:
        model = Category
        # fields = ['id', 'name']
        fields = "__all__"
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
        

class ProductSerializerForInvoice(ModelSerializer):
    variants = VariantSerializer(source='variant', read_only=True,many=True)
    offer_price = serializers.ReadOnlyField(source='get_offer_price')
    thumb_url = serializers.ReadOnlyField(source='thumb.get_url')
    discount = serializers.SerializerMethodField()
    class Meta:
        model = Products
        fields = ['id','name','thumb','sku','is_show_website','variants','offer_price','price','discount','stock','thumb_url',]
    
    def get_discount(self, obj):
        return 0


# class ProductCreateUpdateUtils():
#     def validate(self, data):
#         sku = data.get('sku')
#         if self.instance is not None:
#             existing_product = Products.objects.filter(sku=sku).exclude(id=self.instance.id).first()
#         else:
#             existing_product = Products.objects.filter(sku=sku).first()
#         print("existing_product12323434",existing_product)
#         # if existing_product:
#         #     raise serializers.ValidationError('A product with this SKU already exists.')
#         return data

class ProductCreateUpdateUtils():
    # ...

    def create_attributes_values(self, data):
        data = data.get('attribute_value')
        attribute_values = []
        for attribute_value_data in data:
            attribute_id = attribute_value_data.pop('attribute')
            value = attribute_value_data.pop('value')
            try:
                attribute_id = attribute_id.id
            except:
                attribute_id = attribute_id
            attribute = Attributes.objects.get(id=attribute_id)  # Retrieve the attribute instance
            # attribute_value_queryset = AttributeValue.objects.filter(attribute=attribute, value__iexact=value, **attribute_value_data)
            # if attribute_value_queryset.exists():
            #     attribute_value = attribute_value_queryset.first()
            # else:
            attribute_value = AttributeValue.objects.create(attribute=attribute, value=value, **attribute_value_data)
            attribute_values.append(attribute_value)
        return attribute_values

    # ...
    def update_attribute_values(self, data):
        attribute_values_list = []
        attribute_values = data
        for attrs in attribute_values:
            att_val_serializer = AttributeValueSerializer(data=attrs)
            if att_val_serializer.is_valid():
                att_val_serializer.save()
                attribute_values_list.append(att_val_serializer.data.get('id'))
        return attribute_values_list
        # return attribute_values
    def create_variants(self, data):
        variants = []
        for variant_data in data:
            attribute_values = self.create_attributes_values(variant_data)
            variant_data.pop('attribute_value') 
            images = variant_data.pop('images',[])
   

            try:
                stock = variant_data.get('stock')
                if stock == None:
                    raise serializers.ValidationError({'stock - variant': ['This field can not be null.']})
            except:
                pass
            # if len(images) == 0:
            #     raise serializers.ValidationError({'images': ['Please select atleast one image for variant.']})
            name = variant_data.get('name')
            price = variant_data.get('price')
            stock = variant_data.get('stock')
            is_active = variant_data.get('is_active')
 
            updated_stock = 0 if stock == None else stock 
            
            variant = Variant.objects.create(name=name,price=price,stock=updated_stock,is_active=is_active)
                
            for attribute_value in attribute_values:
                variant.attribute_value.add(attribute_value.id) 
            for image in images:
                try:
                    variant.images.add(image.id) 
                except:
                    variant.images.add(image)   
            variants.append(variant)
        return variants
    

    def update_variants(self, variant_data, instance):
        variants = []
        for data in variant_data:
            images = data.pop('images',[])
            stock = data.get('stock')
            updated_stock = 0 if stock == None else stock 

            # if len(images) == 0:
            #     raise serializers.ValidationError({'images': ['Please select atleast one image for variant.']})
            attribute_values = self.update_attribute_values(data.get('attribute_value'))
            variant = Variant.objects.filter(id=data.get('id')).first()
            variant.attribute_value.set(attribute_values)
            variant.images.set(images)
            variant.name = data.get('name')
            variant.price = data.get('price')
            variant.stock = updated_stock
            variant.is_active = data.get('is_active')

            variant.save()
            variants.append(variant.id)
        return variants

        # return attribute_values_list

    
    def create_or_get_tags(self, data):
        tags = []
        for tag_data in data:
            tag_queryset = Tags.objects.filter(name=tag_data['name'])
            if tag_queryset.exists():
                tag = tag_queryset.first()
            else:
                tag = Tags.objects.create(**tag_data)
            tags.append(tag)
        return tags


class RelatedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'name', 'slug', 'sku', ]

class ProductSerializerForStatusUpdate(serializers.Serializer):
    products = serializers.ListField(child=serializers.IntegerField(),write_only=True)
    is_new_arrival = serializers.BooleanField(write_only=True)
    is_trending = serializers.BooleanField(write_only=True)



class ProductSerializer(serializers.ModelSerializer,ProductCreateUpdateUtils):
    variant_details = VariantSerializer(source='variant', read_only=True,many=True)
    tag_details = TagSerializer(source='tags', read_only=True,many=True)
    category_details = CategorySerializer(source='category', read_only=True,many=True)
    thumb_url = serializers.ReadOnlyField(source='get_thumb_url')
    thumb_url2 = serializers.ReadOnlyField(source='get_thumb_url2')
    variant_chart_url = serializers.ReadOnlyField(source='get_variant_chart_url')
    variant =VariantSerializer(many=True)
    tags = TagSerializer(many=True)
    rating = serializers.ReadOnlyField(source = "get_rating")
    discount = serializers.ReadOnlyField(source='get_discount')
    related_products_details = RelatedProductSerializer(source='related_products', read_only=True,many=True)
    feature_images_details = DocumentSerializer(source='get_feature_images', read_only=True,many=True)
    variants_json = serializers.SerializerMethodField()
    variant_json_previous = serializers.SerializerMethodField()
    barcode = serializers.ReadOnlyField(source='get_barcode_url')

    class Meta:
        model = Products
        fields = '__all__'
        read_only_fields = ['slug','barcode','qrcode']

    def get_variant_json_previous(self, obj):
        return obj.variants_json
    
    def create_default_values(self, data):
        attribute,created = Attributes.objects.get_or_create(name="Default")
        # attribute_value,created = AttributeValue.objects.get_or_create(attribute=attribute, value="Default")
        attribute_value = AttributeValue.objects.filter(attribute=attribute, value="Default").first()
        if not attribute_value:
            attribute_value = AttributeValue.objects.create(attribute=attribute, value="Default")
        variant = Variant.objects.create(stock=data.get('stock'),price=0,name="Default")
        variant.attribute_value.add(attribute_value)
        variant.save()
        return [variant]

    def get_variants_json(self, obj):
        from coreapp.helper import print_log


        variants = obj.variant.all().order_by('stock')
        variant_json = {
            'mainState': {},
            'AttributesInputValue': {}
        }

        for variant in variants:
            attribute_values = variant.attribute_value.all().order_by('-created_at')
            color_values = []

            for attribute_value in attribute_values:
                color_values.append(attribute_value.value)

            print_log(f"-------------color values {variant.name} {variant.id} -------------------")
            print_log(color_values)
            print_log("-------------color values-------------------\n")

            variant_data = {
                'is_active': variant.is_active,
                'variant_action':variant.is_active,
                'variant_stock': str(variant.stock),
                'variant_name': variant.name,
                'attribute_value': [
                    {
                        'attribute': 'Color',
                        'value': color_value
                    } for color_value in color_values
                ],
                'variant_price': str(variant.price),
                "images": [id for id in variant.images.all().values_list('id',flat=True)],
                "img_details": [
                {
                    "id": images.id,
                    "url": images.get_url
                }for images in variant.images.all()
            ]
            }

            for color_value in color_values:
                if color_value not in variant_json['mainState']:
                    variant_json['mainState'][color_value] = []
                variant_json['mainState'][color_value].append(variant.name)
                variant_json['AttributesInputValue'][variant.name] = variant_data
            variant_json['mainState']={}
            for variant in obj.variant.all():
                for attribute in variant.attribute_value.all():
                    attribute_name = attribute.attribute.name
                    if attribute_name not in variant_json['mainState']:
                        variant_json['mainState'][attribute_name] = []
                    if attribute.value not in variant_json['mainState'][attribute_name]:
                        variant_json['mainState'][attribute_name].append(attribute.value)


        return variant_json


    # def get_variants_json(self, obj):
    #     variants_json = []

    #     for variant in obj.variant.all().order_by('stock'):
    #         attribute_values = variant.attribute_value.all().order_by('-created_at')
    #         attributes_data = {}

    #         for attribute_value in attribute_values:
    #             attribute_name = attribute_value.attribute.name
    #             attribute_value_data = {
    #                 'attribute': attribute_name,
    #                 'value': attribute_value.value,
    #             }
    #             attributes_data[attribute_name] = attribute_value_data

    #         variant_data = {
    #             'is_active': variant.is_active,
    #             'variant_stock': str(variant.stock),
    #             'variant_name': variant.name,
    #             'variant_price': str(variant.price),
    #             "images": list(variant.images.all().values_list('id', flat=True)),
    #             "img_details": [{"id": img.id, "url": img.get_url} for img in variant.images.all()],
    #             'attributes': attributes_data,
    #         }

    #         variants_json.append(variant_data)

    #     return variants_json
    # def get_variants_json(self, obj):
    #     main_state = {}
    #     attributes_input_value = {}

    #     for variant in obj.variant.all().order_by('stock'):
    #         attribute_values = variant.attribute_value.all().order_by('-created_at')

    #         for attribute_value in attribute_values:
    #             attribute_name = attribute_value.attribute.name
    #             value = attribute_value.value
                
    #             if attribute_name not in main_state:
    #                 main_state[attribute_name] = set()
    #             main_state[attribute_name].add(value)
                
    #         color_attribute_values = main_state.get("color", set())
    #         for color in color_attribute_values:
    #             # attribute_name = attribute_value.attribute.name
    #             # value = attribute_value.value
    #             variant_name = f"{color}"
    #             variant_data = {
    #                 'is_active': True if variant.is_active else False,
    #                 'variant_action': True if variant.is_active else False,
    #                 'variant_stock': str(variant.stock),
    #                 'variant_name': variant_name,
    #                 'variant_price': str(variant.price),
    #                 "images": list(variant.images.all().values_list('id', flat=True)),
    #                 "img_details": [{"id": img.id, "url": img.get_url} for img in variant.images.all()],
    #                 'attributes': [
    #                     {
    #                         'color': color,
    #                         'size': values,
    #                     } for values in main_state.get("size", set())
    #                 ],
    #             }
    #             attributes_input_value[variant_name] = variant_data

    #     main_state_result = {}
    #     for attribute_name, attribute_values in main_state.items():
    #         main_state_result[attribute_name] = sorted(attribute_values)

    #     return {
    #         'mainState': main_state_result,
    #         'AttributesInputValue': attributes_input_value,
    #     }



    def create(self, validated_data):
        try:
            variant = validated_data.pop('variant')
            if(len(variant) == 0):
                variant_data = self.create_default_values(validated_data)
            else:
                variant_data = self.create_variants(variant)
            tags_data = self.create_or_get_tags(validated_data.pop('tags'))
            categories = validated_data.pop('category')
            feature_images = validated_data.pop('feature_images',[])
            related_products = validated_data.pop('related_products',[])
            removed_products = validated_data.pop('removed_products',[])
            is_update_related = validated_data.get('is_update_related',False)
            print_log("----------Before Product Create----------------")
            product = Products.objects.create(**validated_data)
            print_log("----------After Product Create----------------")

            product.variant.set(variant_data)
            product.category.set(categories)
            product.related_products.set(related_products)
            product.removed_products.set(removed_products)
            product.tags.set(tags_data)
            product.feature_images.set(feature_images) 
            product.is_update_related = True
            product.save()
        except Exception as e:
            print_log("----------ERROR IN PRODUCT CREATE----------------")
            print_log(str(e))
            print_log("----------ERROR IN PRODUCT CREATE----------------\n\n")

        return product 


        
class ProductSerializer_Update(serializers.ModelSerializer,ProductCreateUpdateUtils):
    variant_update_info = serializers.ListField(child=serializers.DictField(),write_only=True)
    # variant_details = VariantSerializer(source='variant', read_only=True,many=True)
    variant_details = VariantSerializer(source='variant', read_only=True,many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Products
        fields = '__all__'
        read_only_fields = ['slug','barcode','qrcode']

    def update(self, instance, validated_data):
        variant_data = validated_data.pop('variant_update_info',None) 
        tags = validated_data.pop('tags',None)
        related_products = validated_data.pop('related_products',[])
        removed_products = validated_data.pop('removed_products',[])
        if variant_data:
            self.instance.variant.clear()
            if variant_data:
                for variant in variant_data:
                    variant_id = variant.get('id',None)
                    if variant_id is None:
                        variant_no_id = self.create_variants([variant])
                        instance.variant.add(variant_no_id[0])

                    else:
                        variant_with_id = self.update_variants([variant],instance)
                        instance.variant.add(variant_with_id[0])
        if tags:
            tags_data = self.create_or_get_tags(tags)
            instance.tags.set(tags_data)
        if related_products:
            instance.related_products.set(related_products)
        elif related_products == []:
            instance.related_products.clear()
        if removed_products:
            instance.removed_products.set(removed_products)
        instance.is_update_related = False
        instance.save()
        instance = super(ProductSerializer_Update,self).update(instance, validated_data)
        return instance

class CategorySerializerForProduct(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductListSerializer(serializers.ModelSerializer):
    thumb_url = serializers.ReadOnlyField(source='get_thumb_url')
    thumb_url2 = serializers.ReadOnlyField(source='get_thumb_url2')
    category_details = CategorySerializerForProduct(source='category', read_only=True,many=True)
    # thumb_resized = serializers.ReadOnlyField(source="get_thumb_resized_url")
    tag_details = TagSerializer(many=True,source = 'tags',read_only=True)
    


    class Meta:
        model = Products
        fields = ['id', 'name', 'category','main_category','tag_details','description','is_show_website','category_details', 'thumb_url', 'thumb_url2', 'stock', 'slug', 'sku', 'price', 'is_active', "updated_at", ]
    




class AttributeSerializer(ModelSerializer):
    class Meta:

        model = Attributes
        fields = "__all__"


class CustomerSerializer(ModelSerializer):
    total_purchase = serializers.ReadOnlyField(source="total")
    count = serializers.ReadOnlyField(source="invoice_count_method")
    invoice_number = serializers.ReadOnlyField(source="get_invoice_numbers")
    redex_division_details = RedexDivisionSerializerMinimal(read_only=True,source='redex_division')
    redex_district_details = RedexDistrictSerializerMinimal(read_only=True,source='redex_district')
    redex_area_details = RedexAreaSerializerMinimal(read_only=True,source='redex_area')
    class Meta:

        model = Customer
        fields = "__all__"
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
        

class CustomerSerializerForInvoice(ModelSerializer):
    class Meta:
        model = Customer
        fields ='__all__'
        # fields = ["id", "name", "email", "mobile", "total_purchase", "status"]


class BulkProductSerializer(serializers.Serializer):
    file = serializers.FileField()