
from . import serializers
from ...models import *
from coreapp.models import User
from coreapp.helper import *
from .. import filters as custom_filters
from coreapp.renderers import CustomRenderer, ProductRenderer
from django.db.models import Exists, OuterRef
from ... import constants
class ProductAPI(viewsets.ModelViewSet):
    queryset = Products.objects.filter(is_show_website=True).order_by('order')
    serializer_class = serializers.ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class  = custom_filters.ProductFilter
    search_fields = ['name','sku']
    lookup_field = 'slug'
    http_method_names = ['get']
    renderer_classes = [ProductRenderer,]

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ProductListSerializerForWeb
        return serializers.ProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @paginate
    def get_paginated_products(self):
        queryset = self.filter_queryset(self.get_queryset())
        sorted_products = sorted(
                queryset, key=lambda product: float(product.get_offer_price())
            )
        if self.request.query_params.get("sort_by") == str(constants.ProductSortChoices.PRICE_HIGH_TO_LOW):
            sorted_products =  sorted(
                queryset,
                key=lambda product: float(product.get_offer_price()),
                reverse=True,
            )
        return sorted_products
    def list(self, request, *args, **kwargs):
        sort_by = self.request.query_params.get("sort_by",None)
        if sort_by and int(sort_by) in [3,4]:
            return self.get_paginated_products()
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def slugs(self, request):
        product_slugs = Products.objects.filter(is_show_website=True).values_list('slug', flat=True)
        category_slugs = Category.objects.filter(is_active=True).values_list('slug', flat=True)
        slugs = {
            "product_slugs":product_slugs,
            "category_slugs":category_slugs
        }
        return Response(slugs, status=status.HTTP_200_OK)

class CategoryAPI(viewsets.ModelViewSet):
    '''
class MainCategoryChoices(models.IntegerChoices):
    HOME_DECOR = 0, _("Home Decor")
    IN_STYLE = 1, _("In Style")

class SubMainCategoryChoices(models.IntegerChoices):
    FOR_DINING = 0, _("For Dining")
    FOR_LIVING = 1, _("For Living")
    CASUAL_WEAR = 2, _("Casual Wear")
    PARTY_WEAR = 3, _("Party Wear")
    EXCLUSIVE_WEAR = 4, _("Exclusive Wear")
    FOOT_WEAR = 5, _("Foot Wear")
    FOR_COUPLES = 6, _("For Couples")
    KIDS_ZONE = 7, _("Kids Zone")
    '''
    queryset = Category.objects.filter(is_active=True)
    serializer_class = serializers.CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']
    # filterset_fields = ['level','main_category','sub_main_category','category_type']
    filterset_class  = custom_filters.CategoryFilterWeb
    lookup_field = 'slug'
    http_method_names = ['get']
    renderer_classes = [ProductRenderer,]

 

    @action(detail=False, methods=['get'])
    def sub_categories(self, request):
        querysets = super().get_queryset()

        categories = Category.objects.filter(is_active=True,sub_main_category=None)
        categories_with_count = categories.annotate(sub_category_count=Count('sub_main_category_new'))
        cats_list = categories_with_count.filter(sub_category_count__gt=0,is_active=True)
                
        home_decor = cats_list.filter(main_category=0)
        in_style = cats_list.filter(main_category=1)
        home_decor_serializer = serializers.AllCategorySerializerWithSubCats(home_decor,many=True)
        in_style_serializer = serializers.AllCategorySerializerWithSubCats(in_style,many=True)
        response_data = {
            "home_decor":home_decor_serializer.data,
            "in_style":in_style_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    # def list(self, request, *args, **kwargs):
    #     main_category = self.request.query_params.get("main_category")
    #     queryset =  self.queryset.annotate(
    #     has_subcategories=Exists(
    #         self.queryset.objects.filter(sub_main_category=OuterRef("id"))
    #     )
    # ).filter(has_subcategories=True)
        
    #     return super().list(request, *args, **kwargs)
    # @paginate
    # def get_category_with_no_category(self,category_type,main_category):
    #     queryset =  self.queryset.annotate(
    #             has_subcategories=Exists(
    #                 self.queryset.filter(sub_main_category=OuterRef("id"))
    #             )
    #         ).filter(has_subcategories=True,category_type=category_type,main_category=main_category)
    #     return queryset
    # def list(self, request, *args, **kwargs):
    #     category_type = self.request.query_params.get("category_type")
    #     main_category = self.request.query_params.get("main_category")
    #     if category_type is not None:
    #         return self.get_category_with_no_category(category_type,main_category)
    #     return super().list(request, *args, **kwargs)



class AttributeAPI(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Attributes.objects.all()
    serializer_class = serializers.AttributeSerializer
    http_method_names = ['get']
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    

class AttributeValueAPI(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = AttributeValue.objects.all()
    serializer_class = serializers.AttributeValueSerializer
    http_method_names = ['get']

class TagsAPI(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Tags.objects.all()
    serializer_class = serializers.TagsSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = custom_filters.TagsFilter


class HomepageAPI(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Products.objects.all()
    serializer_class = serializers.ProductListSerializerForWebMinimal
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    def list(self, request, *args, **kwargs):
        from promotions.models import Banner
        from promotions.api.web.serializers  import BannerSerializerMinimal
        main_category = self.request.query_params.get("main_category",0)
        max = self.request.query_params.get("max",5)
        main_category= int(main_category) 
        products = Products.objects.filter(is_show_website=True,main_category=main_category)
        new_arrival = products.filter(is_show_website=True,is_new_arrival=True).order_by('?')[:max]
        offers = products.filter(offer__isnull=False)[:max]
        trending = (products.annotate(total_sold=Sum("invoice_products__quantity"))
                .order_by("-total_sold")
                .order_by("is_trending")
            )[:5]
        banner = Banner.objects.filter(is_active=True,main_category=main_category)[:max]
        response_data = {
            "new_arrival":serializers.ProductListSerializerForWeb(new_arrival,many=True).data,
            "trending":serializers.ProductListSerializerForWeb(trending,many=True).data,
            "offers":serializers.ProductListSerializerForWeb(offers,many=True).data,
            "banner":BannerSerializerMinimal(banner,many=True).data,
        }
        return Response(response_data, status=status.HTTP_200_OK)