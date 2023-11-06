from django_filters import rest_framework as rest_filter
from ..models import *
from rest_framework import serializers
from ..constants import *
from django.db.models import F, Value, DecimalField
from django.db.models.functions import Coalesce

class OutletProductFilter(rest_filter.FilterSet):
    query = rest_filter.CharFilter(
        method="get_query_product", label="Search"
    )

    class Meta:
        model = OutLetProducts
        fields =['outlet','product','query','is_return','status']

    def get_query_product(self, queryset, name, value):
        return queryset.filter(Q(product__name__icontains=value) | Q(product__sku__icontains=value)).distinct()


class ProductFilter(rest_filter.FilterSet):
    min_price = rest_filter.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = rest_filter.NumberFilter(field_name="price", lookup_expr="lte")
    is_offer = rest_filter.BooleanFilter(
        field_name="client",
        method="filter_is_offer",
        label="is_offer",
    )
    sort_by = rest_filter.ChoiceFilter(
        method="filter_sort_by",
        choices=ProductSortChoices.choices,
        label="Sort by (0:Popularity, 1:Rating, 2:Latest, 3:Price Low to High, 4:Price High to Low, 5:Trending)",
    )
    sort_by_attribute = rest_filter.CharFilter(
        method="filter_sort_by_attribute", label="Sort by attribute"
    )
    related_products = rest_filter.CharFilter(
        method="filter_related_products", label="Related Products"
    )

    frequently_bought_together = rest_filter.CharFilter(
        method="filter_frequently_bought_together",
        label="Frequently Bought Together",
    )
    class Meta:
        model = Products
        fields = [
            "min_price",
            "max_price",
            "category",
            "main_category",
            "tags",
            "variant",
            "is_new_arrival",
            "price",
        ]

    def filter_is_offer(self, queryset, name, value):
        from django.utils import timezone
        current_datetime = timezone.now()
        offers = Offer.objects.filter(is_active=True, start_date__lte=current_datetime, expiry_date__gte=current_datetime)
        products = offers.values_list("product", flat=True)
        categories = offers.values_list("category", flat=True)
        products =  queryset.filter(Q(id__in=products) | Q(category__in=categories))
        return products

    def filter_sort_by(self, queryset, name, value):
        value = str(value)
        if value == str(ProductSortChoices.POPULARITY):
            products = queryset.annotate(
                total_sold=Sum("invoice_products__quantity")
            ).order_by("-total_sold")
            # for product in products:
            #     print(product.name, product.total_sold)
            return products
        elif value == str(ProductSortChoices.RATING):
            return queryset.annotate(avg_rating=Avg("review__star")).order_by(
                "-avg_rating"
            )
        elif value == str(ProductSortChoices.LATEST):
            return queryset.order_by("-created_at")
        elif value == str(ProductSortChoices.PRICE_LOW_TO_HIGH):
            return queryset

        elif value == str(ProductSortChoices.PRICE_HIGH_TO_LOW):
            
            return queryset
        elif value == str(ProductSortChoices.TRENDING):
            most_sold = (
                queryset.annotate(total_sold=Sum("invoice_products__quantity"))
                .order_by("-total_sold")
                .order_by("is_trending")
            )
            return most_sold
            # return most_sold
        else:
            return queryset.order_by("-created_at")

    def filter_sort_by_attribute(self, queryset, name, value):
        ids = value.split(",")
        return queryset.filter(variant__attribute_value__id__in=ids).distinct()
    
    def filter_related_products(self, queryset, name, value):
        product = Products.objects.get(id=value)
        categories = product.category.all()
        query_data =  queryset.filter(category__in=categories).exclude(id=value)
        if query_data.count() < 1:
            query_data = queryset.filter(main_category=product.main_category).exclude(id=value)
        return query_data
    
    def filter_frequently_bought_together(self, queryset, name, value):
        product = Products.objects.get(id=value)
        query_data = queryset.annotate(total_sold=Sum("invoice_products__quantity")).order_by("-total_sold").order_by("is_trending").exclude(id=value).filter(main_category=product.main_category)
        if query_data.count() < 1:
            query_data = queryset.filter(main_category=product.main_category).exclude(id=value)
        return query_data



class AttributeFilter(rest_filter.FilterSet):
    product = rest_filter.CharFilter(
        method="filter_by_product", label="filter_by_product"
    )

    class Meta:
        model = Attributes
        fields = "__all__"

    def filter_by_product(self, queryset, name, value):
        pass


class TagsFilter(rest_filter.FilterSet):
    category = rest_filter.ChoiceFilter(
        method="filter_by_product",
        choices=MainCategoryChoices.choices,
        label="Sort by (0:Home Decor, 1:In Style)",
    )

    class Meta:
        model = Tags
        fields = "__all__"

    def filter_by_product(self, queryset, name, value):
        prods = Products.objects.filter(main_category=int(value))
        tags = []
        for prod in prods:
            for tag in prod.tags.all():
                tags.append(tag.id)
        return queryset.filter(id__in=tags).distinct()


class CategoryFilterWeb(rest_filter.FilterSet):
    sub_main_category_slug = rest_filter.CharFilter(
        method="filter_by_sub_main_category_slug",
        label="filter_by_sub_main_category_slug",
    )

    class Meta:
        model = Category
        fields = [
            "level",
            "main_category",
            "sub_main_category",
            "category_type",
            "sub_main_category_slug",
        ]

    def filter_by_sub_main_category_slug(self, queryset, name, value):
        return queryset.filter(sub_main_category__slug=value)
