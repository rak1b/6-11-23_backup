from inventory.models import *
from rest_framework import serializers
from ...models import *
from coreapp.api.serializers import DocumentSerializer
from django.db.models import Max, Min


class CategorySerializer(serializers.ModelSerializer):
    thumb_url = serializers.ReadOnlyField(source='get_thumb_url')
    # has_categories = serializers.ReadOnlyField(source='has_categories')

    class Meta:
        model = Category
        fields = ['id', 'name','slug','has_categories','thumb_url', 'main_category','sub_main_category',]
class AllCategorySerializer(serializers.ModelSerializer):
    class   Meta:
        model = Category
        fields = ['id', 'name','slug']
class AllCategorySerializerWithSubCats(serializers.ModelSerializer):
    sub_categories = AllCategorySerializer(source='other_categories', read_only=True,many=True)
    class   Meta:
        model = Category
        fields = ['id', 'name','slug','sub_categories']

    
class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attributes
        fields = '__all__'
    
class AttributeValueSerializer(serializers.ModelSerializer):
    attribute_details = AttributeSerializer(source='attribute', read_only=True)
    class Meta:
        model = AttributeValue
        fields = '__all__'
    
class VariantSerializer(serializers.ModelSerializer):
    attribute_value_details = AttributeValueSerializer(source='attribute_value', read_only=True,many=True)
    image_details = DocumentSerializer(source='images', read_only=True,many=True)
    product_name = serializers.ReadOnlyField(source='get_product.name')
    product_slug = serializers.ReadOnlyField(source='get_product.slug')
    product_id = serializers.ReadOnlyField(source='get_product.id')

    class Meta:
        model = Variant
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    variant_details = VariantSerializer(source='get_active_variants', read_only=True,many=True)
    related_variant_details = VariantSerializer(source='get_related_product_variants', read_only=True,many=True)
    tag_details = TagSerializer(source='tags', read_only=True,many=True)
    category_details = CategorySerializer(source='category', read_only=True,many=True)
    thumb_url = serializers.ReadOnlyField(source='get_thumb_url')
    discount = serializers.ReadOnlyField(source='get_discount')
    discount_type_text = serializers.ReadOnlyField(source='get_discount_type')
    offer_price = serializers.ReadOnlyField(source='get_offer_price')
    is_in_wishlist = serializers.SerializerMethodField()
    feature_image_details = DocumentSerializer(source='get_feature_images_web', read_only=True,many=True)
    related_feature_image_details = DocumentSerializer(source='get_related_feature_images_web', read_only=True,many=True)
    variant_chart = serializers.ReadOnlyField(source='get_variant_chart_url')
    class Meta:
        model = Products
        fields = '__all__'

    def get_is_in_wishlist(self, obj):
        request = self.context.get('request', None)
        from promotions.models import Wishlist
        if request:
            user = request.user
            if user.is_authenticated:
                return Wishlist.objects.filter(user=user,product=obj).exists()
            else:
                return False
        return False
    

class ProductListSerializerForWeb(serializers.ModelSerializer):
    thumb_url = serializers.ReadOnlyField(source='get_thumb_url')
    thumb_url2 = serializers.ReadOnlyField(source='get_thumb_url2')
    offer_price = serializers.ReadOnlyField(source='get_offer_price')
    discount = serializers.ReadOnlyField(source='get_discount')
    discount_type_text = serializers.ReadOnlyField(source='get_discount_type_text')
 
    class Meta:
        model = Products
        fields = ['id','name','slug','sku','thumb_url','thumb_url2','price','offer_price','discount','discount_type_text','description','is_new_arrival',]

class ProductListSerializerForWebMinimal(serializers.ModelSerializer):
    thumb_url = serializers.ReadOnlyField(source='get_thumb_url')
    thumb_url2 = serializers.ReadOnlyField(source='get_thumb_url2')

    class Meta:
        model = Products
        fields = ['name','slug','thumb_url','thumb_url2']

class ProductListSerializer(serializers.ModelSerializer):
    thumb_url = serializers.ReadOnlyField(source='get_thumb_url')
    thumb_url2 = serializers.ReadOnlyField(source='get_thumb_url2')
    discount_type = serializers.ReadOnlyField(source='get_discount_type')
    discount_type_text = serializers.ReadOnlyField(source='get_discount_type_text')
    offer_price = serializers.ReadOnlyField(source='get_offer_price')
    discount = serializers.ReadOnlyField(source='get_discount')
    is_in_wishlist = serializers.SerializerMethodField()
    thumb_url = serializers.ReadOnlyField(source='get_thumb_url')
    variant_details = VariantSerializer(source='get_active_variants', read_only=True,many=True)
    related_variant_details = VariantSerializer(source='get_related_product_variants', read_only=True,many=True)
    variant_chart = serializers.ReadOnlyField(source='get_variant_chart_url')
    feature_image_details = DocumentSerializer(source='get_feature_images_web', read_only=True,many=True)

    class Meta:
        model = Products
        fields = ['name','slug','sku','is_show_website','description','feature_image_details','is_new_arrival','thumb_url','thumb_url2','variant_details','related_variant_details','variant_chart','price','stock','id','discount_type_text','discount_type','offer_price','discount','is_in_wishlist']
    


    def get_is_in_wishlist(self, obj):
        request = self.context.get('request', None)
        from promotions.models import Wishlist
        if request:
            user = request.user
            if user.is_authenticated:
                return Wishlist.objects.filter(user=user,product=obj).exists()
            else:
                return False
        return False
    
class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        exclude = ['created_at','updated_at','attribute']
    

class AttributeSerializer(serializers.ModelSerializer):
    values = AttributeValueSerializer(source='get_values', read_only=True,many=True)
    # values = serializers.ListField(child=serializers.CharField(),source='get_values')
    class Meta:
        model = Attributes
        exclude = ['created_at','updated_at']
        
        
        

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        exclude = ['created_at','updated_at']



