from inventory.models import *
from rest_framework import serializers
from ...models import *
from inventory.api.web.serializers import *
class OfferSerializer(serializers.ModelSerializer):
    products_details = ProductListSerializer(many=True, read_only=True,source='get_all_products')
    category_details = CategorySerializer(many=True, read_only=True,source='category')
    class Meta:
        model = Offer
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_thumb_url = serializers.ReadOnlyField(source='reviewed_by.get_image_url')
    class Meta:
        model = Review
        fields = '__all__'

class BannerSerializer(serializers.ModelSerializer):
    image_details = DocumentSerializer(read_only=True,source='image')
    class Meta:
        model = Banner
        fields = '__all__'

class BannerSerializerMinimal(serializers.ModelSerializer):
    image_url=serializers.ReadOnlyField(source='image.get_url')
    class Meta:
        model = Banner
        fields = ['image_url']