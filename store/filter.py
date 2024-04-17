from django_filters.rest_framework import FilterSet

from store.models import Product

class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields  = {
            'collection_id': ['exact'],
            'unit_price': ['gt', 'lt']
        }
        # we use a dictionary instead if an array so we can specify
        # how the filtering should be done