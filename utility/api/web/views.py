
from . import serializers
from ...models import *
from coreapp.models import User
from coreapp.helper import *
from .. import filters as custom_filters
from utility.utils import sslcommerz_utils
from rest_framework import filters
class ContactUsWEBAPI(viewsets.ModelViewSet):

    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post']

class PageAPI(viewsets.ModelViewSet):
    queryset = Page.objects.filter(is_active=True)
    serializer_class = serializers.PageSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get']
    filterset_class = custom_filters.PageFilter

class PaymentAPI(ModelViewSet):
    permission_classes = [AllowAny]
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        session_info = sslcommerz_utils.get_session()
        if session_info['status'] == 'FAILED':
            return Response({'message': session_info['failedreason']}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'session':  session_info['sessionkey'], 'redirectGatewayURL': session_info['GatewayPageURL']})
    
    @action(detail=False, methods=['get'], url_path='status')
    def status(self, request):
        # Implement your custom view logic here
        session_key = request.query_params.get('session')
        payment_status_response = sslcommerz_utils.get_payment_status(session_key)
        response_data = {
            'session_key': session_key,
            'payment_status': payment_status_response,
        }

        return Response(response_data)

class GlobalSettingsAPI(views.APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(
        responses={200: serializers.GlobalSettingsSerializer}
    )
    def get(self, request):
        global_settings = GlobalSettings.objects.first()
        serializer = serializers.GlobalSettingsSerializer(global_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)

class subscription(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Subscription.objects.all()
    serializer_class = serializers.SubscriptionSerializer
    http_method_names = ['post']



class PageAdminAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Page.objects.all()
    serializer_class = serializers.PageSerializer
    http_method_names = ['get']


class SocialMediaAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = SocialMedia.objects.all()
    serializer_class = serializers.SocialMediaSerializer
    http_method_names = ['get']


class TestimonialAdminAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Testimonial.objects.all()
    serializer_class = serializers.TestimonialSerializer
    http_method_names = ['get']


 

class TeamMemberAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = TeamMember.objects.all()
    serializer_class = serializers.TeamMemberSerializer
    http_method_names = ['get']

class ContactUsAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'email', 'phone', 'message']
    filterset_fields = ['contact_type']


class DisplayCenterAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Display_Center.objects.all()
    serializer_class = serializers.DisplayCenterSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description', 'mobile']


class GetDeliveryChargeAPI(APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(request=serializers.GetDeliveryChargeSerializer)
    def post(self, request):
        data = request.data
        upazilla_id= data.get('upazilla_id')
        inside_dhaka = GlobalSettings.objects.first().inside_dhaka
        outside_dhaka = GlobalSettings.objects.first().outside_dhaka
        delivery_charge = CustomDeliveryCharge.objects.filter(upazilla__id=upazilla_id).first()
        if delivery_charge:
            return Response({'delivery_charge': delivery_charge.price,'found_in_json':True,'custom':2}, status=status.HTTP_200_OK)
        else:
            upazilla = Upazilla.objects.filter(id=upazilla_id).first()
            if not upazilla:
                return Response({'delivery_charge': outside_dhaka,'found_in_json':False,'custom':2}, status=status.HTTP_200_OK)
            if upazilla.name=="Dhaka City" or upazilla.id == '1001':
                return Response({'delivery_charge': inside_dhaka,'found_in_json':True,'custom':0}, status=status.HTTP_200_OK)
            else:
                return Response({'delivery_charge': outside_dhaka,'found_in_json':True,'custom':1}, status=status.HTTP_200_OK)
            
from . import serializers
from ...models import *
from coreapp.models import User
from coreapp.helper import *
from .. import filters as custom_filters
from utility.utils import sslcommerz_utils
from rest_framework import filters
class ContactUsWEBAPI(viewsets.ModelViewSet):

    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post']

class PageAPI(viewsets.ModelViewSet):
    queryset = Page.objects.filter(is_active=True)
    serializer_class = serializers.PageSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get']
    filterset_class = custom_filters.PageFilter

class PaymentAPI(ModelViewSet):
    permission_classes = [AllowAny]
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        session_info = sslcommerz_utils.get_session()
        if session_info['status'] == 'FAILED':
            return Response({'message': session_info['failedreason']}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'session':  session_info['sessionkey'], 'redirectGatewayURL': session_info['GatewayPageURL']})
    
    @action(detail=False, methods=['get'], url_path='status')
    def status(self, request):
        # Implement your custom view logic here
        session_key = request.query_params.get('session')
        payment_status_response = sslcommerz_utils.get_payment_status(session_key)
        response_data = {
            'session_key': session_key,
            'payment_status': payment_status_response,
        }

        return Response(response_data)

class GlobalSettingsAPI(views.APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(
        responses={200: serializers.GlobalSettingsSerializer}
    )
    def get(self, request):
        global_settings = GlobalSettings.objects.first()
        serializer = serializers.GlobalSettingsSerializer(global_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)

class subscription(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Subscription.objects.all()
    serializer_class = serializers.SubscriptionSerializer
    http_method_names = ['post']



class PageAdminAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Page.objects.all()
    serializer_class = serializers.PageSerializer
    http_method_names = ['get']


class SocialMediaAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = SocialMedia.objects.all()
    serializer_class = serializers.SocialMediaSerializer
    http_method_names = ['get']


class TestimonialAdminAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Testimonial.objects.all()
    serializer_class = serializers.TestimonialSerializer
    http_method_names = ['get']


 

class TeamMemberAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = TeamMember.objects.all()
    serializer_class = serializers.TeamMemberSerializer
    http_method_names = ['get']

class ContactUsAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'email', 'phone', 'message']
    filterset_fields = ['contact_type']


class DisplayCenterAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Display_Center.objects.all()
    serializer_class = serializers.DisplayCenterSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description', 'mobile']


class GetDeliveryChargeAPI(APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(request=serializers.GetDeliveryChargeSerializer)
    def post(self, request):
        data = request.data
        upazilla_id= data.get('upazilla_id')
        inside_dhaka = GlobalSettings.objects.first().inside_dhaka
        outside_dhaka = GlobalSettings.objects.first().outside_dhaka
        delivery_charge = CustomDeliveryCharge.objects.filter(upazilla__id=upazilla_id).first()
        if delivery_charge:
            return Response({'delivery_charge': delivery_charge.price,'found_in_json':True,'custom':2}, status=status.HTTP_200_OK)
        else:
            upazilla = Upazilla.objects.filter(id=upazilla_id).first()
            if not upazilla:
                return Response({'delivery_charge': outside_dhaka,'found_in_json':False,'custom':2}, status=status.HTTP_200_OK)
            if upazilla.name=="Dhaka City" or upazilla.id == '1001':
                return Response({'delivery_charge': inside_dhaka,'found_in_json':True,'custom':0}, status=status.HTTP_200_OK)
            else:
                return Response({'delivery_charge': outside_dhaka,'found_in_json':True,'custom':1}, status=status.HTTP_200_OK)
            
from . import serializers
from ...models import *
from coreapp.models import User
from coreapp.helper import *
from .. import filters as custom_filters
from utility.utils import sslcommerz_utils
from rest_framework import filters
class ContactUsWEBAPI(viewsets.ModelViewSet):

    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post']

class PageAPI(viewsets.ModelViewSet):
    queryset = Page.objects.filter(is_active=True)
    serializer_class = serializers.PageSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get']
    filterset_class = custom_filters.PageFilter

class PaymentAPI(ModelViewSet):
    permission_classes = [AllowAny]
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        session_info = sslcommerz_utils.get_session()
        if session_info['status'] == 'FAILED':
            return Response({'message': session_info['failedreason']}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'session':  session_info['sessionkey'], 'redirectGatewayURL': session_info['GatewayPageURL']})
    
    @action(detail=False, methods=['get'], url_path='status')
    def status(self, request):
        # Implement your custom view logic here
        session_key = request.query_params.get('session')
        payment_status_response = sslcommerz_utils.get_payment_status(session_key)
        response_data = {
            'session_key': session_key,
            'payment_status': payment_status_response,
        }

        return Response(response_data)

class GlobalSettingsAPI(views.APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(
        responses={200: serializers.GlobalSettingsSerializer}
    )
    def get(self, request):
        global_settings = GlobalSettings.objects.first()
        serializer = serializers.GlobalSettingsSerializer(global_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)

class subscription(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Subscription.objects.all()
    serializer_class = serializers.SubscriptionSerializer
    http_method_names = ['post']



class PageAdminAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Page.objects.all()
    serializer_class = serializers.PageSerializer
    http_method_names = ['get']


class SocialMediaAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = SocialMedia.objects.all()
    serializer_class = serializers.SocialMediaSerializer
    http_method_names = ['get']


class TestimonialAdminAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Testimonial.objects.all()
    serializer_class = serializers.TestimonialSerializer
    http_method_names = ['get']


 

class TeamMemberAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = TeamMember.objects.all()
    serializer_class = serializers.TeamMemberSerializer
    http_method_names = ['get']

class ContactUsAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'email', 'phone', 'message']
    filterset_fields = ['contact_type']


class DisplayCenterAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Display_Center.objects.all()
    serializer_class = serializers.DisplayCenterSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description', 'mobile']


class GetDeliveryChargeAPI(APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(request=serializers.GetDeliveryChargeSerializer)
    def post(self, request):
        data = request.data
        upazilla_id= data.get('upazilla_id')
        inside_dhaka = GlobalSettings.objects.first().inside_dhaka
        outside_dhaka = GlobalSettings.objects.first().outside_dhaka
        delivery_charge = CustomDeliveryCharge.objects.filter(upazilla__id=upazilla_id).first()
        if delivery_charge:
            return Response({'delivery_charge': delivery_charge.price,'found_in_json':True,'delivery_charge_type':2}, status=status.HTTP_200_OK)
        else:
            upazilla = Upazilla.objects.filter(id=upazilla_id).first()
            if not upazilla:
                return Response({'delivery_charge': outside_dhaka,'found_in_json':False,'delivery_charge_type':2}, status=status.HTTP_200_OK)
            if upazilla.name=="Dhaka City" or upazilla.id == '1001':
                return Response({'delivery_charge': inside_dhaka,'found_in_json':True,'delivery_charge_type':0}, status=status.HTTP_200_OK)
            else:
                return Response({'delivery_charge': outside_dhaka,'found_in_json':True,'delivery_charge_type':1}, status=status.HTTP_200_OK)
            