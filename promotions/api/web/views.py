
from . import serializers
from ...models import *
from coreapp.helper import *
from rest_framework.permissions import IsAuthenticated, AllowAny

class OfferAPI(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = serializers.OfferSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get']

class ReviewAPI(viewsets.ModelViewSet):
    queryset = Review.objects.filter(is_active=True)
    serializer_class = serializers.ReviewSerializer
    permission_classes = [AllowAny,]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product',]
    http_method_names = ['get','post']
    

    
    
class BannerAPI(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = serializers.BannerSerializer
    permission_classes = [AllowAny,]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name','main_category']
    search_fields = ['name','description']
    http_method_names = ['get']