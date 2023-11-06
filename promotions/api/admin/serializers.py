from inventory.models import *
from rest_framework import serializers
from ...models import *
from inventory.api.inventory.serializers import ProductListSerializer,CategorySerializerForProducts
from coreapp.api.serializers import DocumentSerializer
from coreapp.helper import print_log
class OfferSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(read_only=True,source='get_all_products',many=True)
    category_details = CategorySerializerForProducts(source='category',read_only=True,many=True)
    banner_url = serializers.ReadOnlyField(source='get_banner_url')
    class Meta:
        model = Offer
        fields = '__all__'

    def validate(self, attrs):
        from promotions.models import Offer
        from inventory.models import Products,Category
        from datetime import datetime
        current_datetime = datetime.now()
        offer = Offer.objects.filter(is_active=True, start_date__lte=current_datetime, expiry_date__gte=current_datetime)
        product = attrs.get('product')
        category = attrs.get('category')
        if self.instance:
            offer = offer.exclude(id=self.instance.id)
        if product:
            product_ids = [p.id for p in product]
            product_categories = Products.objects.filter(id__in=product_ids).values_list('category', flat=True)
            product_categories = list(set(product_categories))
            prod_offer =offer.filter(product__in=product_ids)
            if  prod_offer.count() > 0:
                product_names = prod_offer.values_list('product__name',flat=True)
                str_product_names = ",".join(product_names)
                raise serializers.ValidationError(f"This products {str_product_names} already has an offer ")
            cat_offer =offer.filter(category__in=product_categories)
            if cat_offer.count() > 0:
                cat_names = cat_offer.values_list('category__name',flat=True)
                str_cat_names = ",".join(cat_names)
                raise serializers.ValidationError(f"This product's categories {str_cat_names} already has an offer")

        if category:
            cat_offer = offer.filter(category__in=category)
            cat_names = cat_offer.values_list('category__name',flat=True)
            str_cat_names = ",".join(cat_names)
            if cat_offer.count() > 0:
                raise serializers.ValidationError(f"This categories {str_cat_names} already has an offer")
            
            product_ids = Products.objects.filter(category__in=category).values_list('id',flat=True)
            prod_offer = offer.filter(product__in=product_ids)
            product_names = prod_offer.values_list('product__name',flat=True)
            str_product_names = ",".join(product_names)
            if prod_offer.count() > 0:
                raise serializers.ValidationError(f"This products {str_product_names} from given categories already has an offer ")

        return super().validate(attrs)



class ReviewSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(read_only=True,source='product')
    photos_details = DocumentSerializer(read_only=True,source='photos',many=True)
    reviewed_by_name = serializers.ReadOnlyField(source='reviewed_by.get_full_name')
    reviewer_thumb_url = serializers.ReadOnlyField(source='reviewed_by.get_image_url')

    class Meta:
        model = Review
        fields = '__all__'

class BannerSerializer(serializers.ModelSerializer):
    image_details = DocumentSerializer(read_only=True,source='image')

    def validate(self, attrs):
        from promotions.models import Banner
        order = attrs.get('order')
        banner = Banner.objects.filter(order=order,is_active=True,main_category=attrs.get('main_category'))
        if self.instance:
            banner = banner.exclude(id=self.instance.id)
        if banner.count() > 0:
            raise serializers.ValidationError(f"Another banner already exists with order {order},please change order")
        return super().validate(attrs)
    class Meta:
        model = Banner
        fields = '__all__'