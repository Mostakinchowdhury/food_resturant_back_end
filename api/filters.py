# filters.py
import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    tag = django_filters.CharFilter(field_name='tags__name', lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    class Meta:
        model = Product
        fields = [] 
