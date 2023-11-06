
from . import serializers
from ...models import *
from coreapp.models import User
from coreapp.helper import *



class OutletAPI(viewsets.ModelViewSet):
    queryset = Outlet.objects.all()
    serializer_class = serializers.OutletSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active',]
    search_fields = ['name','mobile','email',]
    ordering = ['-created_at']


class ChalanAPI(viewsets.ModelViewSet):
    queryset = Chalan.objects.all()
    serializer_class = serializers.ChalanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['outlet',]
    search_fields = ['number','outlet__name','outlet__mobile','outlet__email',]
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action=="retrieve":
            return serializers.ChalanSerializerForInvoice
        return serializers.ChalanSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        if self.action=="retrieve":
            context['outlet'] = self.get_object().outlet

        return context
