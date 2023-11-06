from inventory.models import *
from rest_framework import serializers
from ...models import *
from coreapp.api.serializers import SignupSerializer
from coreapp.models import BillingInfo
from utility.api.admin.serializers import *
class BillingInfoSerializer(serializers.ModelSerializer):
    redex_division_details = RedexDivisionSerializerMinimal(read_only=True,source='redex_division')
    redex_district_details = RedexDistrictSerializerMinimal(read_only=True,source='redex_district')
    redex_area_details = RedexAreaSerializerMinimal(read_only=True,source='redex_area')
    
    class Meta:
        model = BillingInfo
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    item = CartItemSerializer(many=True)
    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = ['user','is_paid']


class CartSerializerForCreateInCheckout(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = ['is_paid']

class CheckoutSerializerForShow(serializers.ModelSerializer):
    billing_info_details = BillingInfoSerializer()
    cart_details = CartSerializer()

    class Meta:
        model = Checkout
        fields = '__all__'
        read_only_fields = ['billing_info']


class CheckoutSerializer(serializers.ModelSerializer):
    # billing_info = BillingInfoSerializer()
    cart = CartSerializer()
    password = serializers.CharField(write_only=True,required=False,allow_blank=True)

    class Meta:
        model = Checkout
        fields = '__all__'
        read_only_fields = ['user','session_key','tran_id']
    
    def check_stock(self, data):
        cart = data.get('cart')
        if cart.get('item') == []:
            raise serializers.ValidationError("Cart is empty")
        else:
            for data in cart.get("item",[]):
                product = Products.objects.get(id=data.get('product').id)
                if product.stock < data.get('quantity'):
                    raise serializers.ValidationError(f"{product.name.upper()} - This product is out of stock")
                variant = Variant.objects.get(id=data.get('variant').id)
                if variant.stock < data.get('quantity'):
                    raise serializers.ValidationError(f"{variant.name.upper()} - This variant is out of stock")


    def create_user(self,data):
        try:
            signup_data = {
                'first_name': data['shipping_first_name'],
                'last_name': data['shipping_last_name'],
                'email': data['shipping_email'],
                'mobile': data['shipping_mobile'],
                'password': data['password'],
                'confirm_password': data['password'],
                'billing_info': self.create_billing_info(data),
                'is_customer': True,

            }
        except Exception  as e:
            raise serializers.ValidationError(f"{e} This field is missing")
        user_serializer = SignupSerializer(data=signup_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        return user

    
    def create_billing_info(self, billing_data):
        data = {
            'first_name': billing_data['shipping_first_name'],
            'last_name': billing_data['shipping_last_name'],
            'company_name': billing_data['shipping_company_name'],
            'country': billing_data['shipping_country'],
            'district': billing_data['shipping_district'],
            'division': billing_data['shipping_division'],
            'street_address': billing_data['shipping_street_address'],
            'town_city': billing_data['shipping_town_city'],
            'state_county': billing_data['shipping_state_county'],
            'postcode_zip': billing_data['shipping_postcode_zip'],
            'mobile': billing_data['shipping_mobile'],
            'email': billing_data['shipping_email'],
            
        }
        billing_info_serializer = BillingInfoSerializer(data=data)
        billing_info_serializer.is_valid(raise_exception=True)
        billing_info = billing_info_serializer.save()
        return billing_info
    
    def create_cart_items(self, cart_items_data):
        print("cart_items_data",cart_items_data)
        data = []
        for items in cart_items_data:
            items['product'] = items['product'].id
            items['variant'] = items['variant'].id
            cart_items_serializer = CartItemSerializer(data=items)
            cart_items_serializer.is_valid(raise_exception=True)
            cart_items = cart_items_serializer.save()
            data.append(cart_items.id)
        return data

    def create_cart(self, validated_data):
        cart_data = validated_data.pop('cart')
        cart_data['item'] = self.create_cart_items(cart_data['item'])
        cart_data['user'] = validated_data['user'].id if validated_data['user'] else None
        cart_serializer = CartSerializerForCreateInCheckout(data=cart_data)
        cart_serializer.is_valid(raise_exception=True)
        cart = cart_serializer.save()
        return cart

    def create(self, validated_data):
        self.check_stock(validated_data)
        request = self.context.get('request')
        create_account = validated_data.get('create_account')
        if create_account:
            current_user = self.create_user(validated_data)
        else:
            current_user = request.user
        if current_user.is_anonymous:
            current_user = None
        #     raise serializers.ValidationError("Either login or check the create account box")
        validated_data['user'] = current_user
        validated_data['cart'] = self.create_cart(validated_data)
        try:
            validated_data.pop('password') #removed password from validated_data
        except:
            pass
        checkout = super().create(validated_data)
        return checkout


class VerifyCouponSerializer(serializers.ModelSerializer):
    products = serializers.ListField(child=serializers.IntegerField())
    class Meta:
        model = Coupon
        fields = ['code','products']