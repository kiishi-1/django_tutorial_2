from decimal import Decimal
from store.models import Cart, CartItem, Customer, Order, OrderItem, Product, Collection, Review
from rest_framework import serializers


# a serializer is an object that knows how to convert a model instance to a dictionary
# you need 2 sets of representation of a model instance
# internal and external
# external is what is going to be used outside(contains the attribute of the model you choose show)
# internal contains all attribute
class CollectionSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']
    #you want to mark the product_count field as read only when
    # defining it because it's not used for creating or updating a collection
    product_count = serializers.IntegerField(read_only=True)

class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    # using max_length=255 cus we'll use this serializer when receiving data from our api
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
    # unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    
    # serializing relationships
    # collection = serializers.PrimaryKeyRelatedField(
    #     queryset=Collection.objects.all()
    # )
    # we can include the primary key or ID of each collection in the product object

    # collection = serializers.StringRelatedField()
    # django will convert each collection to a string object and return it
    # cus of this
    # def __str__(self) -> str:
        # return self.title
    # to change the string representation of an object in python we override the
    # __str__ mtd 
    #  def __str__(self) -> str is type annotation it's ssying the mtd returns a string object
    # and then access the title

    # another way - including a nested object
    # collection = CollectionSerializer()
    # it'll be rendered as an object
    # for example
    # "collection" : {
    #   "id" : 5,
    #   "title" : "Stationary"
    # }

    # another way - including a hyperlink to an endpoint for viewing that collection
    collection = serializers.HyperlinkedRelatedField(
        queryset=Collection.objects.all(),
        view_name='collection-detail'
        # this argument is used for generating hyperlinks
    )

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)
        # Decimal(1.1) wrapping 1.1(float) to make it decimal

class ProductSerializer2(serializers.ModelSerializer):
    # this is done so we don't have to redefine all the fields all the time
    class Meta:
        model =  Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection']
        # this is done so we don't have to redefine all the fields all the time
        # so django will go to the Product class and look up the 
        # definition of the fields in the array
        # and automatically create a product serializer
        # we get {
        # "id": 648,
        # "title": "7up Diet, 355 Ml",
        # "unit_price": 79.07,
        # "collection": 5
        # }
        # for collection which is a related field we have a primary key related field
        # so by default model serializers use primary key by default
        # we can always override it however way we want 
        # collection = serializers.HyperlinkedRelatedField(
        # queryset=Collection.objects.all(),
        # view_name='collection-detail'
        # # this argument is used for generating hyperlinks
        # )
        # with this we'll convert each collection to hyperlink
        # {"collection": "http://127.0.0.1:8000/store/collections/5/"}
        # we can use "price" instead of "unit_price"
        # fields = ['id', 'title', 'price', 'collection']
        # price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
        # fields = __all__
        # to add all the fields
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)
    # validation at the object level
    # validating the request data can involve comparing multple fields
    # our validation rules comes from the definition of model fields
    # to use other validation mtd we need override validate mtd in our serializer
    # the mtd is ctually defined in the model serializer class
    # def validate(self, data):
    #     if data['password'] != data['confirm_password']:
    #         return serializers.ValidationError('Passwords do not match')
    #     return data
        # data is a dictionary

        
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        # fields = ['id', 'date', 'name', 'description', 'product']
        # for product which is a related field we have a primary key related field
        # so by default model serializers use primary key by default
        # we don't want to have to specify a product when creating a review
        # {
        #     "name": "a",
        #     "description": "a",
        #     "product": 1
        # }
        fields = ['id', 'date', 'name', 'description']
        # but product(product_id) cannot be null
        # we are going to use our get_serializer_context in the ReviewViewSet
        # to get the product_id from the url
        # check ReviewViewSet
        
        # in our serializer we are going to override the create mtd for 
        # creating a review to get the product_id from the url
        # instead of relying on the default implementation that will simply
        # get the values of the fields, we instead going to provide our own implementation
        
    def create(self, validated_data):
        #here we extract the product id 
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)
        # product_id= is from the product field in the Review model
        # **validated_data is for unpacking the validated data dictionary
        # that we receive
    
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    # we don't want to just return the product id
    # we will be able to return the entire fields of the product class
    # available in the serializer

    # if we don't want to use the object gotten from using the prdoct serializer as it is
    # i.e we don't want to show somethings or want to add sonethings later 
    # we create another serializer of the combination of the product and cart item serializer
    # on second thought, i don't think it's that deep. it just to use a simpler serializer

    # we need a different serializer for adding an item to shopping cart
    # cus we don't want to be able to affect the product details
    # so we can make the product serializer read only product = SimpleProductSerializer(read_only=True)
    # and we'll need to add product_id to our fields but that just create redundancy
    # cus we'll have both the product field and product_id field
    # we don't want to create redundacy when writing our code
    # so we use a new serializer in our view set but we don't want to hard code it
    # we want to dynamically return a serializer depending on the request
    total_price = serializers.SerializerMethodField()
    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
        # items is the related name for the
        # reverse relationship of cart and cartitem
        # we are gettin a list of items (multiple instances)

        #you want to mark the id field as read only when
    # defining it because it's not sending to the server only reading from the server
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    # when you use many=True in a serializer,
    # it indicates that the serializer is expected to handle
    #  multiple instances of the associated model
    # it's indicating that the items field is expected to be a list of CartItem instances.
    total_price = serializers.SerializerMethodField()
    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
        # [item for item in collection]
        # this is a list comprehension
        # cart.items returns a manager object and using all(), we get a queryset
        # which returns all it's items
        # for each item in the list(collection) we want to return quantity * unit price
        # we get a list of totals and the we sum them all up
    

class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']
    
    
    # to explicitly define the product_id field
    product_id = serializers.IntegerField()
    # the object being sent to the server will be
    #     {
    #     "product_id": null,
    #     "quantity": null
    # }
    # in this serializer we can't rely on the the default implementation of the save mtd
    # cus we want to cater for when the same product 
    # is being added to the same cart multiple times, we don't want to
    # create multiple cart item records, we want to update the quantity of and 
    # existing item i.e increase the number of items even if it's the same product 
    # added to the cart. we're just increasing the number of that particular product
    # instead of creating another record(row) for it

    # validating individual fields
    # the field you want to validate must come after the validate name
    # i.e validate_product_id.
    # value is the value(object) we are validating
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given ID was found')
        return value
    # we don't need to do this for quantity cus in our serializer
    # we are referencing the quantity field of our CartItem model
    # we made quantity of PositiveSmallIntegerField which takes care of validation
    # to take it to the next level PositiveSmallIntegerField(validator=[MinValueValidator(1)])
    # we're setting the minimum value to 1
    def save(self, **kwargs):
        #here we extract the product id and quantity
        # under the hood, there's a call to serializers.is_valid()
        # when the data gets validated then we can get it 
        # from an attribute called serializers.validated_data
        # which is a dictionary
        # since we are inside our serializer class we use self
        product_id = self.validated_data['product_id']
        # we're reading the product id we get from the client and storing it
        # inside the product_id variable
        quantity = self.validated_data['quantity']
        # cart id is not in the request it's available in the url.
        # we don't have access to the url parameters in the serializer
        # we have to pass it fromour view set to the serializer
        #here we extract the product id 
        cart_id = self.context['cart_id']

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id, quantity=quantity)
            # update an existing item
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # create a new item
            #  **validated_data
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
            # cart_item = CartItem.objects.create(cart_id=cart_id, product_id=product_id, quantity=quantity)
            # is redundant instead we unpack **self.validated_data dictionary

        return self.instance

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

# building the user profile api
# we are implementing this in the store app cus this is where
# we defined the customer
class CustomerSerializer(serializers.ModelSerializer):
    # the user_id attribute is created dynamically at runtime, so we need
    # to explicitly define it or else it won't reflect on content field in the apiview 
    user_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']

class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']
        # we are not including the order field cus we are using this serializer 
        # inside the order serializer

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    # when you use many=True in a serializer,
    # it indicates that the serializer is expected to handle
    #  multiple instances of the associated model
    # it's indicating that the items field is expected to be a list of OrderItem instances.
    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', "items"]

# when creating an order all we have to send to the server is the cart id
# we can't use the order serializer cus the object has a different structure compare to
# the object we want to send to the server, check the fields. 
# so we need a new serializer 
        
class CreateOrderSerializer(serializers.Serializer):
    # we are not using serializer.ModelSerializer cus we are not using 
    # a Meta class based on the Order model. cart id is not a field in 
    # the model class. so instead of using serializer.ModelSerializer we'll use
    # serializer.Serializer meaning we don't need the Meta class
    cart_id = serializers.UUIDField()
    
    def save(self, **kwargs):
        print(self.validated_data['cart_id'])

        # to get the user id
        print(self.context['user_id'])
        (customer, created) = Customer.objects.get_or_create(user_id=self.context['user_id'])
        # using get_or_create in in the save mtd is not in violation of the command query separation principle
        # cus we can change the state of the system the save mtd
        # the save mtd is a command not a query
        Order.objects.create(customer=customer)
        # we are passing the customer object cus the customer field is the only 
        # field in the Order model that's we need to set
        # unlike placed_at which is set automatically, payment_status which has a default value
        # return super().save(**kwargs)
