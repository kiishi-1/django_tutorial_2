from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework import status
from store.filter import ProductFilter
from store.pagination import DefaultPagination
from store.permissions import FullDjangoModelPermissions, IsAdminOrReadOnly, ViewCustomerHistoryPermission
from .models import Cart, CartItem, Customer, Order, OrderItem, Product, Collection, Review
from .serializer import AddCartItemSerializer, CartItemSerializer, CartSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductSerializer, ProductSerializer2, CollectionSerializer, ReviewSerializer, UpdateCartItemSerializer
from django.db.models.aggregates import Count

# Create your views here.

class ProductList(APIView):
    def get(self, request):
        query_set = Product.objects.select_related('collection').all()
        serializer = ProductSerializer2(query_set, many=True, context={'request': request})
        return Response(serializer.data)
        
    def post(self, request):   
        serializer = ProductSerializer2(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# a mixin is a class that encapsulate a pattern of code 
# examples are ListModelMixin, CreateModelMixin
# in ListModelMixin, we have an inbuilt mtd for listing a bunch of models
# a query set is basically being created
# a serializer is also being created and we are returning the serialized data
# in CreateModelMixin, we have a create mtd the encapsulate the logic for 
# creating a resource. in the mtd we are creating a serializer, then we validate the
# incoming data. Next we have a call to perform create mtd which is where 
# serializer.save() is called.
# we are getting the success header and the we're returning the response with the serialized data
# and the 201 status
# all these is very similar to our code pattern
# there are more mixins for performing operations on resources
# most of the time we are not going to use the mixins directly instead we
# use concrete classes that combine one or more mixins called generic views
#  for example ListCreateAPIView which combine ListModelMixin and CreateModelMixin
class ProductList2(ListCreateAPIView):
    # use these attribute when you don't have extra logic to implement
    # queryset = Product.objects.select_related('collection').all()
    # select_related('collection') was used to preload the collection, so that we
    # can use the title field but we don't need it here
    queryset = Product.objects.all()
    serializer_class = ProductSerializer2
    # there's no attribute for specifying serializer_context

    # overriding mtds
    # inbuilt mtds
    # use a mtd if you want to use some logic or condition like checking the 
    # current user
    # def get_queryset(self):
    #     return Product.objects.select_related('collection').all()
    
    # def get_serializer_class(self):
    #     return ProductSerializer2
    
    def get_serializer_context(self):
        return {'request': self.request}
  
class ProductDetails2(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer2
    # get and put mtd is completely implemented in the retrieve and update mixin 
    # in the RetrieveUpdateDestroyAPIView

    # lookup_field = 'id'
    # for specifying our the name of the url parameter
    
    # here we have some logic specific to our application
    # none of the mixins in django know about product, orderitems and there count
    # we need to override the deleted mtd we inherited from the RetrieveUpdateDestroyAPIView class

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    

class ProductDetails(APIView):
    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer2(product, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer2(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, id):
        product = get_object_or_404(Product, pk=id)
        if product.orderitems.count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)        

class ProductViewSet(ModelViewSet):
    #view set, a set of related views, is used to combine the logic of related views
    # inside a single class

    # we are getting all products when we trigger this endpoint http://127.0.0.1:8000/store/products/
    # but what of if we want to filter this products, let say filter them by a specific collection
    # we should be able to pass a query string parameter http://127.0.0.1:8000/store/products/?collection_id=1
    # we should be able to see all product in this collection
    # so we can't use this queryset = Product.objects.all()
    # we'll have to override the get_queryset mtd 

    # note: django uses the queryset attribute to figure out the basename by default
    # if it is not specified in the router register in the url.py file
    # queryset = Product.objects.all()

    # what of if in addition to collection you want to filter the product by another field
    # we can use a third party library called django filter
    # so we can easily filter any models by any field we don't have to hard code the filtering logic

    queryset = Product.objects.all()
    serializer_class = ProductSerializer2
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['collection_id', 'unit_price']
    filterset_class = ProductFilter
    # pagination_class = PageNumberPagination
    # we specify the page size in the settings.py file
    # we can set it globally in the settings.py file so there'll be no need to use the pagination_class filed
    # in every view set
    # REST_FRAMEWORK = {
    #     'COERCE_DECIMAL_TO_STRING': False,
    #     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    #     'PAGE_SIZE': 10
    # }
    pagination_class = DefaultPagination
    # we are doing this to rectify the warning(check DefaultPagination for the warning)
    # by using a custom pagination class since we are not specifying a default paginatin class
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title', 'description']
    # search_fields = ['title', 'description', 'collection__title']
    # collection__title is used to reference the title field in the collection class(related class)
    # so when we search we find any product that has the key search word

    ordering_fields = ['unit_price', 'last_update']

    # def get_queryset(self):
    #     # Product.objects.filter(collection_id=self.request.query_params['collection_id'])
    #     # we are not returning it directly like this cus it won't work
    #     # we need a condition just in case we don't have a collection id i.e when we're not 
    #     # trying to filter the query set with the collection_id
    #     queryset = Product.objects.all()
    #     # collection_id = self.request.query_params['collection_id']
    #     # request.query_params['collection_id'] or request.query_params.get('collection_id') is
    #     #  what we are using to make the get request i.e ?collection=

    #     collection_id = self.request.query_params.get('collection_id')
    #     # 'collection_id'
    #     # using the .get mtd returns none by default if we don't have a key by the collection_id name 
    #     if collection_id is not None:
    #         # we can use the collection_id argument cus of the Product model has a collection field
    #         queryset = queryset.filter(collection_id=collection_id)
    #     return queryset

    def get_serializer_context(self):
        return {'request': self.request}

    #earlier on we were overriding the delete mtd cus we were using RetrieveUpdateDestroyAPIView
    # now we are using ModelViewSet
    # in the RetrieveUpdateDestroyAPIView class delete mtd 
    # that simply delegate(returns) the destroy mtd
    # but then we combined the ProductList and ProductDetails class into a view set
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    # the destroy mtd is inbuilt into the DestroyModelMixin
    # we are not using product = get_object_or_404(Product, pk=pk) cus
    # inside the mtd we have a call to get object 'instance = self.get_object()'
    # it returns the object we are looking for(like a specific product)
    # the product is retrieved from our DB and we don't want to retrieve it twice



    # def delete(self, request, pk):
    #     product = get_object_or_404(Product, pk=pk)
    #     if product.orderitems.count() > 0:
    #         return Response({'error': 'Product cannot be deleted because it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     product.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

@api_view()
# if api_view is used here the request the product_list function is taking 
# will be an instance of the request class that comes with the rest framework
# it'll replace the request object in django with the new request object  
# that comes with the rest_framework which is simpler and more powerful
def product_lis(request):
    # return HttpResponse('ok')

    # http://127.0.0.1:8000/store/products/, when we put it 
    # in our browser we can see the browsable api which we can
    # use to test our api endpoints in the browser
    # a client app(ex mobile or web app) hits our endpoints we won't see the browsable api
    # it'll only see the data in the response
    return Response('ok')

@api_view(['GET', 'POST'])
# GET is supported by default that's why we didn't have to pass it in previously
def product_list(request):
    if request.method == 'GET':
        query_set = Product.objects.select_related('collection').all()
        serializer = ProductSerializer2(query_set, many=True, context={'request': request})
        # many=True is tell the serializer that it's taking in a query set
        # so that it'll iterate over the query set and convert each object to a dictionary
        return Response(serializer.data)
    elif request.method == 'POST':
        # deserializing objects
        # this is the opposite of serialization and it happens when we receive data
        # from the client 
        # if a client wants to create a new product
        # to do this we should send a post request to the products endpoint
        # and in the body of the request you should include a product object
        # on the server we have to read the data on the body of the request
        # and deserialize it so we can get a product object and store it in the DB
        serializer = ProductSerializer2(data=request.data)
        # when we set this argument 'data=request.data',
        # the ProductSerializer() is going to deserialize the data
        # then the data is going to be available in an attribute called 
        # if serializer.is_valid():
        #     serializer.validated_data
        #     # before we can access this attribute we first have to validate the data
        #     return Response('ok')
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # 400 BAD REQUEST mean the client didn't send valid data to the server

        serializer.is_valid(raise_exception=True)
        serializer.save()
        # saving to the server
        print(serializer.validated_data)
        # OrderedDict([('title', 'a'), ('unit_price', Decimal('1.00')), ('collection', <Collection: collection1>)])
        # this is our valid data attribute. it is an ordered dictionary
        # with 3 key value pairs. title holds  string, unit_price a decimal value and
        # collection, a collaction object
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # django rest_framework takes care of the response and exception

@api_view(['GET', 'PUT', 'DELETE'])
# PATCH  is used to update a subset of an object
# PUT is used to update the entire object 
def product_detail(request, id):
    try:
        product = Product.objects.get(pk=id)
        if request.method == 'GET':
            serializer = ProductSerializer2(product, context={'request': request})
            # the moment we create our serializer, it'll convert our product object to a dictionary
            # and we can get that dictionary from serializer.data
            # we are not using a json renderer cus django will do it under the hood
            # django will create the a json renderer object and then give it the dictionary
            # the json renderer will then convert the dictionary to json object
            # then the json object will end up in the response 
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = ProductSerializer2(product, data=request.data)
            # we will have to pass an instance(instance of product) the serializer
            # will try to update the attribute of that object(product) using
            # the data in the request
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == 'DELETE':
            if product.orderitems.count() > 0:
                return Response({'error': 'Product cannot be deleted because it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# OR
# @api_view()
# def product_details(request, id):
#     product = get_object_or_404(Product, pk=id)
#     serializer = ProductSerializer(product)
#     return Response(serializer.data)

class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(product_count=Count('products'))
    serializer_class = CollectionSerializer
    def get_serializer_context(self):
        return {'request': self.request}
    

class CollectionDetails(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(product_count=Count('products'))
    serializer_class = CollectionSerializer
    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it include one or more products'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  


class CollectionViewSet(ModelViewSet):
    #view set, a set of related views, is used to combine the logic of related views
    # inside a single class
    # if we inherit from ReadOnlyModelViewSet, we will only be able
    # to perform read operations. we can list ll collections or retrieve
    # a single one but are not going to be able to create, update or delete a collection
    queryset = Collection.objects.annotate(product_count=Count('products'))
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    def get_serializer_context(self):
        return {'request': self.request}

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it include one or more products'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  
     

@api_view(['GET', 'POST'])
def collection_list(request):
    if request.method == 'GET':
        query_set = Collection.objects.annotate(product_count=Count('products'))
        serializer = CollectionSerializer(query_set, many=True, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request, pk):
    collection = get_object_or_404(Collection.objects.annotate(product_count=Count('products')), pk=pk)
    # "products" is the related name in the collection field of the Product class
    # it is the reverse relationship
    # each collection as an attribute(field) of 'products'
    if request.method == 'GET':
        serializer = CollectionSerializer(collection, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it include one or more products'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response('ok')


class ReviewViewSet(ModelViewSet):
    # to stop all reviews from being returned regardless of what product we are looking at
    # so we need to apply a filter but not the normal way cus we won't be able to 
    # access the self instance to get the product id from the url
    # to do this we need to override the get queryset mtd
    # queryset = Review.objects.all()
    def get_queryset(self):
        # remember our url has 2 parameter product_pk and pk
        # product primary key and review primary key
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    serializer_class = ReviewSerializer
    # in this view set we have access to url parameters
    # we can use the product_id argument cus of the Review model has a product field
    # so we can read the product(product_id) from the url and using a context object
    # we can pass it to the serializer. we use a context object to provide 
    # additional data to a serializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
        # this is a dictionary that contains our url parameters
        # remember our url has 2 parameter product_pk and pk
        # product primary key and review primary key
        # we've passed this dictionary to our serializer
        # in our serializer we are going to override the create mtd for 
        # creating a review
        # check ReviewSerializer
        # note: we are the product id to access the product object to get the reviews
        # http://127.0.0.1:8000/store/products/1/reviews/


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    # we want to preload the cart with it's items and product
    # we are using prefetch_related and not selected_related cus a cart can have
    # multiple items
    serializer_class = CartSerializer

    # def get_serializer_context(self):
    #     return {'request': self.request}

    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)

# to get the view of the list of items in a cart 
class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    # to set the list of http mtds we want to allow
    # queryset = CartItem.objects.all()
    # serializer_class = CartItemSerializer

    # we want to dynamically return a serializer depending on the request
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
    # we are using cart id to access the cart object to get the items(products)
    # http://127.0.0.1:8000/store/cart/1/reviews/
    
    def get_queryset(self):
        # we want to filter by cart id
        # in this view set we have access to url parameters
        # we are extractiong card id as a url parameter from self.kwargs['cart_pk']
        # kwargs is keyword argument
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')

# building the user profile api
class CustomerViewSet(ModelViewSet):
    # class CustomerViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    # ModelViewSet is not ideal for this view set cus we
    # don't want to support all operation at this endpoint
    # we don't need to list customers, that's only required on the admin panel

    # later on we decided to use ModelViewSet so that the admins can have all 
    # access to all operations at this endpoint (e.g get list(queryset) or delete)
    # but we'll restrict the (particular)operation on the client side


    # here, we should be able to create a customer, retrieve a customer and update
    # we don't need to delete a customer cus when you delete
    # a user, the customer record(row) authomatically gets deleted
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    # permission_classes = [IsAuthenticated]
    # all actions(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet) 
    # in this view set are closed to anonymous users, so only
    # authenticated users can access this
    
    permission_classes = [IsAdminUser]
    # all actions(mtds in ModelViewSet) in this view set are open only to the admins
    # permission_classes = [DjangoModelPermissions]
    # when we apply this permission, the user has to be authenticated and
    # they should have the relevant model permission, that's the permissions created 
    # on the admin panel e.g customer service(which has permissions for adding, deleting changing and viewing customers)
    # and they are stored on the DB in the permissions table
    # this is in a group on the admin panel. a group is a collection of permissions
    # instead of assigning permissions to users one by one, we can just add them to groups.
    
    # permission_classes = [FullDjangoModelPermissions]
    # we don't want to pervent users outside the customer services group from viewing data
    # this is a test apparently, overengineering
    # we want to limit customer management operation to admins, so we use IsAdminUser
    

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAuthenticated()]
    # permissions for CreateModelMixin, RetrieveModelMixin or UpdateModelMixin

    

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    # detail=False is when you want to set the custom action to the list view
    # detail=True is when you want to set the custom action to the detail view
    # recall that most api view as 2 routes
    # one for the list(queryset) - http://127.0.0.1:8000/store/customers/
    # and the other for a selected item in the list(details) - http://127.0.0.1:8000/store/customers/1/
    # permission_classes=[IsAuthenticated] means that only authenticated users
    # can access this method
    # http://127.0.0.1:8000/store/customers/me/ is the endpoint to the current user
    def me(self, request):

        # 'django.contrib.auth.middleware.AuthenticationMiddleware',
        # this middleware inspects the incoming request and if there's
        # info about the user it's going to retrieve that user from the DB
        # and attach it to the request object
        # every request has a user attribute request.user
        # if the user is not logged in it'l be set to an instance of the
        # AnonymousUser class else it's going to be a user object

        (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)
        # customer = Customer.objects.get(user_id=request.user.id)
        # we are using get_or_create instead of get just in case the user doesn't have an account

        # get_or_create object doesn't return acustomer object
        #  it returns a tuple with two values, the customer object and a boolean value
        # that tells us if the object was created or not
        # if left like this an exception "'tuple' object has no attribute 'user_id'." will be thrown
        # so we'll have to unpack it
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        # we are defining a custom action
        # note: all mtds we have or use in a view set 
        # that are responding to requests is call an action
        # for example CreateModelMixin, RetrieveModelMixin, UpdateModelMixin

    # history action for view the history of a particular customer
    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        # pk cus it's for a particular customer
        return Response('ok')


class OrderViewSet(ModelViewSet):
    
    # serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        
        (customer_id, created) = Customer.objects.only('id').get_or_create(user_id=user.id)
        # using get_or_create in in the get_query mtd is in violation of the command query separation principle
        # cus we are not supposed to change the state of the system the get_queryset mtd
        # the get_queryset mtd is a query not a command
        # customer_id is the object we are working with
        # created is the boolean value that check if the object is created or not
        return Order.objects.filter(customer_id=customer_id)
