
from . import serializers
from ...models import *
from coreapp.models import User
from coreapp.helper import *
from ...models import *
from .. import filters

class OutletProductAPI(viewsets.ModelViewSet):
    queryset = OutLetProducts.objects.filter(is_return=False)
    serializer_class = serializers.OutletProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['outlet','product',]
    filterset_class = filters.OutletProductFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.OutletProductSerializerForList
        elif self.action == 'retrieve':
            return serializers.OutletProductSerializerForRetrieve
        return serializers.OutletProductSerializer


    @extend_schema(
        description="create Outlet Products",
        request=serializers.OutletProductSerializer(many=True),
        responses={200: serializers.OutletProductSerializer(many=True)}
    )
    def create(self, request, *args, **kwargs):
        """
        Create multiple Outlet Products with Outlet Variants.
        """
        serializer =  serializers.OutletProductSerializer(data=request.data, many=True,context={'request': request})
        if serializer.is_valid():
            products = serializer.save()
            return Response(serializers.OutletProductSerializerForList(products, many=True).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OutletProductReturnAPI(viewsets.ModelViewSet):
    queryset = OutLetProducts.objects.filter(is_return=True)
    serializer_class = serializers.OutletProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['outlet','product',]
    filterset_class = filters.OutletProductFilter
    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.OutletProductSerializerForList
        elif self.action == 'retrieve':
            return serializers.OutletProductSerializerForRetrieve
        return serializers.OutletProductSerializerForReturn


    @extend_schema(
        description="create Outlet Products",
        request=serializers.OutletProductSerializerForReturn(many=True),
        responses={200: serializers.OutletProductSerializerForList(many=True)}
    )
    def create(self, request, *args, **kwargs):
        """
        Create multiple Outlet Products with Outlet Variants.
        """
        context = {'request': request}
        serializer =  serializers.OutletProductSerializerForReturn(data=request.data, many=True, context=context)
        if serializer.is_valid():
            products = serializer.save()
            return Response(serializers.OutletProductSerializerForList(products, many=True).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
