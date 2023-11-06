
from django.shortcuts import redirect
from . import serializers
from ...models import *
from coreapp.models import User
from coreapp.helper import *
from .. import filters as custom_filters
from rest_framework import status
from utility.utils import sslcommerz_utils
from django.urls import reverse
from coreapp.models import BillingInfo

class BIllingInfoAPI(viewsets.ModelViewSet):
    queryset = BillingInfo.objects.all()
    serializer_class = serializers.BillingInfoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    http_method_names = ['get', 'post', 'put',]

class CheckoutAPI(viewsets.ModelViewSet):
    queryset = Checkout.objects.all()
    serializer_class = serializers.CheckoutSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    http_method_names = ['get', 'post']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request   
        return context
    
    def generate_data(self, checkout_data):
        tran_id = get_random_string(length=10)
        print("tran_id", tran_id)
        url = f"{settings.MEDIA_HOST}/api/v1/order/web/checkout/status/?tran_id={tran_id}"
        print("url1212", url)
        data = {
                'total_amount': checkout_data.total_amount,
                'currency': "BDT",
                'tran_id':tran_id, 
                'success_url': url, # if transaction is succesful, user will be redirected here
                'fail_url':url,# if transaction is failed, user will be redirected here
                'cancel_url':url, # after user cancels the transaction, will be redirected here
                'emi_option': "0",
                'cus_name': checkout_data.shipping_first_name + " " + checkout_data.shipping_last_name,
                'cus_email': checkout_data.shipping_email,
                'cus_phone': checkout_data.shipping_mobile,
                'cus_add1': checkout_data.shipping_street_address,
                'cus_city':  checkout_data.shipping_town_city,
                'cus_country':  checkout_data.shipping_country,
                'shipping_method': "NO",
                'multi_card_name': "",
                'num_of_item': checkout_data.cart.get_product_count(),
                'product_name': checkout_data.cart.get_product_names(),
                'product_category': checkout_data.cart.get_product_categories(),
                'product_profile': "general",
            }
        return data
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        checkout_instance = serializer.save()
        if checkout_instance.payment_type==0:
            return Response({'message': 'Checkout Successful'}, status=status.HTTP_200_OK)
        else:
            data = self.generate_data(checkout_instance)
            session_info = sslcommerz_utils.get_session(data=data)
            if session_info['status'] == 'FAILED':
                return Response({'message': session_info['failedreason']}, status=status.HTTP_400_BAD_REQUEST)
            else:
                checkout_instance.session_key = session_info['sessionkey']
                checkout_instance.tran_id = data['tran_id']
                checkout_instance.save()

            return Response({'session':  session_info['sessionkey'], 'redirectGatewayURL': session_info['GatewayPageURL']})


    @action(detail=False, methods=['get','post'])
    def status(self, request, *args, **kwargs):
        tran_id = self.request.query_params.get('tran_id')
        checkout = Checkout.objects.filter(tran_id=tran_id).first()
        response = sslcommerz_utils.get_payment_status(sessionkey=checkout.session_key)
        from sales.models import Invoice

        if response['status'] == 'VALID':
            try:
                checkout.status = 1
                checkout.total_paid = response['amount']
                checkout.ssl_status = response['status']
                checkout.save()
                cart = Cart.objects.filter(id=checkout.cart.id).first()
                cart.is_paid = True
                cart.save()
                
     
                return redirect(f"{checkout.success_url}?tran_id={tran_id}&status={response['status']}")
            except Exception as e:
              
                print_log(str(e))
                return HttpResponse("Something went wrong. Please try again later.")

        elif response['status'] == 'FAILED':
            return redirect(f"{checkout.success_url}?tran_id={tran_id}&status={response['status']}")
            # return Response({'message': 'Payment Failed'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse("Something went wrong. Please try again later.")
            
class VerifyCouponAPI(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = serializers.VerifyCouponSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        from promotions.models import Offer
        from inventory.models import Products
        data = request.data
        code = data.get('code')
        products = data.get('products',[])

        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid Coupon Code'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Offer.objects.filter(product__in=products).exists():
            return Response({'error': 'Can not add coupon for these products'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            products = Products.objects.filter(id__in=products)
            total_price = products.aggregate(Sum('price'))['price__sum']
            if total_price < coupon.minimum_purchase:
                return Response({'error': f'Minimum purchase amount is {coupon.minimum_purchase}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print_log(str(e))
 
        return Response({'success': 'Coupon is valid','discount':coupon.discount_amount,'id':coupon.id}, status=status.HTTP_200_OK)