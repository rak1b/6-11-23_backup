from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins, views, status
from rest_framework.permissions import IsAdminUser,AllowAny
from rest_framework.response import Response
from django_filters import rest_framework as dj_filters
from . import serializers
from .. import filters
from ...models import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class GlobalSettingsAPI(views.APIView):
    permission_classes = [IsAdminUser, ]

    @extend_schema(
        responses={200: serializers.GlobalSettingsSerializer}
    )
    def get(self, request):
        global_settings = GlobalSettings.objects.first()
        serializer = serializers.GlobalSettingsSerializer(global_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={200: serializers.GlobalSettingsSerializer},request=serializers.GlobalSettingsSerializer )
    def post(self, request):
        global_settings = GlobalSettings.objects.first()
        serializer = serializers.GlobalSettingsSerializer(data=request.data, instance=global_settings)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PageAdminAPI(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, ]
    queryset = Page.objects.all()
    serializer_class = serializers.PageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['page_type','is_active']

class SocialMediaAPI(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, ]
    queryset = SocialMedia.objects.all()
    serializer_class = serializers.SocialMediaSerializer


class TestimonialAdminAPI(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, ]
    queryset = Testimonial.objects.all()
    serializer_class = serializers.TestimonialSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'designation',]

class SliderAdminAPI(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, ]
    queryset = Slider.objects.all()
    serializer_class = serializers.SliderSerializer


class TeamMemberAPI(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, ]
    queryset = TeamMember.objects.all()
    serializer_class = serializers.TeamMemberSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'designation',]

class ContactUsAPI(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, ]
    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'email', 'mobile', 'message']
    filterset_fields = ['contact_type']
    def list(self, request, *args, **kwargs):
        from utility.utils import notification_utils
        notification_utils.update_dashboard_notification("contact_us",0)
        return super().list(request, *args, **kwargs)
    


class DisplayCenterAPI(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, ]
    queryset = Display_Center.objects.all()
    serializer_class = serializers.DisplayCenterSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'location', 'mobile']


class DashboardNotificationAPI(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, ]
    queryset = DashboardNotification.objects.all()
    serializer_class = serializers.DashboardNotificationSerializer
    http_method_names = ['get','patch']

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
class CustomDeliveryChargeAPI(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, ]
    queryset = CustomDeliveryCharge.objects.all()
    serializer_class = serializers.CustomDeliveryChargeSerializer

    def get_serializer_context(self):
        context = {
            'request': self.request,
        }
        return context

class RedexAddressAPI(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = RedexDivision.objects.all()
    serializer_class = serializers.RedexDivisionSerializerList
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['id',]

    def get_serializer_class(self):
        if self.action=="retrieve":
            return serializers.RedexDivisionSerializer
        else:
            return serializers.RedexDivisionSerializerList
    



