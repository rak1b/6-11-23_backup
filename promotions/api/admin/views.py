
from . import serializers
from ...models import *
from coreapp.helper import *

class OfferAPI(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = serializers.OfferSerializer
    permission_classes = [IsAdminUser,]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product',]
    search_fields = ['product__name','name','description']
class ReviewAPI(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [IsAdminUser,]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product','reviewed_by','star']
    search_fields = ['product__name','descriptions']

    def list(self, request, *args, **kwargs):
        from utility.utils import notification_utils
        notification_utils.update_dashboard_notification("review",0)
        return super().list(request, *args, **kwargs)
    
class BannerAPI(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = serializers.BannerSerializer
    permission_classes = [IsAdminUser,]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name']
    search_fields = ['name','description']
