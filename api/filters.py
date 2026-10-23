import django_filters
from api.models import Product


class Productfilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
    )

    max_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
    )

    category = django_filters.NumberFilter(
        field_name='category_id',
    )

    min_stock = django_filters.NumberFilter(
        field_name='stock',
        lookup_expr='gte',
    )

    max_stock = django_filters.NumberFilter(
        field_name='stock',
        lookup_expr='lte',
    )

    class Meta:
        model = Product
        fields = [
            'category',
            'is_active',
            'min_price',
            'max_price',
            'min_stock',
            'max_stock',
        ]