from django.urls import include, path
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers
from . import views
from pprint import pprint
# pprint means pretty printing


# routr = DefaultRouter()
# routr.register('products', views.ProductViewSet)
# # we're saying the 'products' should be manages by the ProductViewSet
# routr.register('collections', views.CollectionViewSet)
# # we're saying the 'collections' should be manages by the CollectionViewSet
# pprint(routr.urls)
# [<URLPattern '^products/$' [name='product-list']>,
#  <URLPattern '^products/(?P<pk>[^/.]+)/$' [name='product-detail']>,
#  <URLPattern '^collections/$' [name='collection-list']>,
#  <URLPattern '^collections/(?P<pk>[^/.]+)/$' [name='collection-detail']>]
# when we use a router to register a route the router registers 
# two patterns, list and detail

# nested routers
router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
# we are specifying the basename cus django uses the 
# queryset attribute in the view set to figure out the basename by default
# but we override it with the get_quaryset mtd and the mtd is to complex for
# django to make a default basename with it
# basename is used as a prefix for generating the name of url patterns
# so our routes are going to be called products-list or products-detail
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('orders', views.OrderViewSet, basename='orders')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
# lookup ?
# The lookup parameter is set to 'product', which means
# that when generating URLs for the nested resource (reviews in this case),
# the lookup will be based on the 'product' field.
# For example, if you have a URL pattern like this for reviews:
# /products/{product_pk}/reviews/
# http://127.0.0.1:8000/store/products/1/reviews/
# The {product_pk} part of the URL represents
# the primary key of the associated 'product'.
# The lookup parameter is specifying the name of this URL parameter.
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')
# basename is used as a prefix for generating the name of url patterns
# so our routes are going to be called product-reviews-list or product-reviews-detail

cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-items')
# so we'll have two routes,  cart-items-list or cart-items-detail

# URLConf
urlpatterns = router.urls + products_router.urls + cart_router.urls 
# urlpatterns = [
#     path(r'', include(router.urls)),
#     path(r'', include(products_router.urls)),
# ]
# urlpatterns = routr.urls

# urlpatterns = [
#     path('products/', views.product_list),
#      path('products/', views.ProductList.as_view()),
#     # path('products/', views.ProductList2.as_view()),
#     as_view convert this class to a regular fn based view
#     path('products/<int:id>/', views.product_detail),
#     # <int:id> is a parameter
#     path('products/<int:id>/', views.ProductDetails.as_view()),
#     #  path('products/<int:pk>/', views.ProductDetails2.as_view()),
#     path('products/<int:id>/', views.ProductDetails2.as_view()),
#     # this will work cus we are using the look_up field in the ProductDetails2 class

#     path('collections/', views.collection_list),
#     #  path('collections/', views.CollectionList.as_view()),
#     path('collections/<int:pk>/', views.collection_detail, name='collection-detail'),
#     #  path('collections/<int:pk>/', views.CollectionDetails.as_view(), name='collection-detail'),
#     # pk cus of django conventions
#     # so the primary key of the collection in the product object
# ]
