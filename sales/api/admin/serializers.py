from inventory.models import *
from rest_framework import serializers
from ...models import *
from inventory.api.admin.serializers import *
class OutletSerializer(serializers.ModelSerializer):
    thumb_url = serializers.ReadOnlyField(source='get_thumb_url')
    class Meta:
        model = Outlet
        fields = "__all__"

class ChalanSerializerForShow(serializers.ModelSerializer):
    products = OutletProductSerializer(many=True, read_only=True,)
    class Meta:
        model = Chalan
        fields = "__all__"



class ChalanSerializerForInvoice(serializers.ModelSerializer):
    chalan_outlet_products_details = OutletProductSerializerForChalanRetrieve(many=True, read_only=True,source='get_chalan_products')
    outlet_name = serializers.ReadOnlyField(source='outlet.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.name')
    last_modified_by_name = serializers.ReadOnlyField(source='last_modified_by.name')
    outlet_location = serializers.ReadOnlyField(source='outlet.location')
    outlet_details = OutletSerializer(read_only=True,source='outlet')
    outlet_product_sku = serializers.SerializerMethodField()
    products_count = serializers.ReadOnlyField(source='get_products_count')
    
    class Meta:
        model = Chalan
        fields = "__all__"
        read_only_fields = ['created_by','number','slug','last_modified_by']
    
    def get_outlet_product_sku(self, obj):
        chalan_products = obj.chalan_outlet_products.all()
        data = {}
        for product in chalan_products:
            data[product.product.sku]=product.id
        return data



class ChalanSerializer(serializers.ModelSerializer):
    chalan_outlet_products_details = OutletProductSerializer(many=True, read_only=True,source='chalan_outlet_products')
    chalan_outlet_products = OutletProductSerializer(many=True, write_only=True)
    outlet_name = serializers.ReadOnlyField(source='outlet.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.name')
    last_modified_by_name = serializers.ReadOnlyField(source='last_modified_by.name')
    outlet_location = serializers.ReadOnlyField(source='outlet.location')
    products_count = serializers.ReadOnlyField(source='get_products_count')

    class Meta:
        model = Chalan
        fields = "__all__"
        read_only_fields = ['created_by','number','slug','last_modified_by']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['last_modified_by'] = user
        chalan_outlet_products = validated_data.pop('chalan_outlet_products')
        for item in chalan_outlet_products:
            item['outlet'] = item['outlet'].id
            item['product'] = item['product'].id
            for variants in item['outletVariant']:
                variants['variant'] = variants['variant'].id
        chalan_outlet_products_serializer = OutletProductSerializer(data=chalan_outlet_products, many=True)
        if chalan_outlet_products_serializer.is_valid():
            chalan_outlet_products_serializer.save()
        else:
            serializers.ValidationError(f"chalan_outlet_products_serializer.errors: {chalan_outlet_products_serializer.errors}")
        chalan_outlet_products_ids = [item['id'] for item in chalan_outlet_products_serializer.data]
        chalan = Chalan.objects.create(**validated_data)
        chalan.chalan_outlet_products.set(chalan_outlet_products_ids)
        chalan.is_chalan_outlet_products_set = True
        chalan.save()
        return chalan