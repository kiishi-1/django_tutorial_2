from django.contrib import admin
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from uuid import uuid4

#Note - django create an id field automatically for each class
#the id field will be the primary key
class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, related_name='+', blank=True)
    #"Product" is a String cus it depends on the Product class which depends on the Collections class and is also created after the Collection class
    #it is hence used for circular relationship cus they depend on each other
    #related_name='+' is to stop reverse relationship from being created, an actual name can be used
    #django authomatically create the reverse relationship of any field created
    #also all these are done to prevent name clash from the reverse relationship being created

    def __str__(self) -> str:
        return self.title
    # to change the string representation of an object in python we override the
    # __str__ mtd 
    #  def __str__(self) -> str is type annotation it's saying the mtd returns a string object

    class Meta:
        ordering = ['title']
        #sorting the collections by their title


class Product(models.Model):
    #to create our custom id field(primary key)
    #sku = models.CharField(max_length=10, primary_key=True)
    #with this django won't create a default primary key
    title = models.CharField(max_length=255)
    #max_length is required
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    # blank=True makes the promotion no longer required so validation will not work on it
    #TextField as in String(long text)
    #no need to set max_length
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(1)])
    #example - 9999.99
    #max_digits and decimal_places are always required for DecimalField
    #always use DecimalField for monetary values
    # MinValueValidator(1) means the lowest value you can get to is 1
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    last_update = models.DateTimeField(auto_now=True)
    #auto_now is so that django automatically stores the current date time
    #auto_now_add is for the first time its used, it'll store the date time the first time it used
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, related_name='products')
    #on_delete=models.PROTECT so that we don't delete the associated product if the collection is delete by mistake
    promotions = models.ManyToManyField(Promotion, blank=True)
    # blank=True makes the promotion no longer required so validation will not work on it

    def __str__(self) -> str:
        return self.title
    # to change the string representation of an object in python we override the
    # __str__ mtd 
    #  def __str__(self) -> str is type annotation it's asying the mtd returns a string object
    class Meta:
        ordering = ['title']
    #sorting the products by their title


class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]
    #upper case to indicate it's fixed list of values, cannot change
    # first_name = models.CharField(max_length=255)
    # last_name = models.CharField(max_length=255)
    # email = models.EmailField(unique=True)
    #unique=True to not end up with duplicate emails
    # we are commenting the fields above cus the user model already has them

    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # you don't want to reference the user model in django of in the core app(custom model)
    # cus

    # def __str__(self):
    #     return f'{self.first_name} {self.last_name}'
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    # to change the string representation of an object in python we override the
    # __str__ mtd 
    #  def __str__(self) -> str is type annotation it's asying the mtd returns a string object

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    
    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        #sorting the customer by their names

        # we want to apply custom model permissions to our APIs
        # so we create a custom permission for our customer model
        permissions = [
            ('view_history', 'can view history')
            # codename(unique identifier) , description
        ]

    # class Meta:
    #     db_table = 'store_customers'
    #     indexes = [
    #         models.Index(fields=['last_name', 'first_name'])
    #     ]
        #indexes, used to speed up queries


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    #on_delete=models.PROTECT so that we don't delete the associated order if the customer is delete by mistake

    # creating custom permissions
    # we do this when we want to make a request that isn't about
    #  creating, updating or deleting data
    class Meta:
        permissions = [
            ('cancel_order', 'can cancel order')
            # codename(unique identifier) , description
            # canceling order is a special kind of request,
            # a special kind of update, so we create a ustom permission for it
        ]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orderitems')
    #on_delete=models.PROTECT so that we don't delete the associated order item if the order or product is delete by mistake
    quantity = models.PositiveSmallIntegerField()
    #PositiveSmallIntegerField prevents negaive values from getting store in this field
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    #we initially declared price in the Product class but we are also doing it here cus price of product can change
    #so we store the price of product at the time it was ordered


#one to one
class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE)
    
    #primary keys don't allow duplicate values
    #if we allow django to create the another id field (primary key), every address is going to have an id meaning we could
    # end up with a one to many relationship cus we can have many addresses with the same customer
    #since customer is the primary key, we can only have one address for each customer cus primary keys don't allow duplicate values
    #on_delete=models.CASCADE means when a customer is deleted, the associated address is also deleted
    #on_delete=models.SET_NULL means when a customer is deleted, the associated address is remains in the database and the customer field is set to null
    #it is used when te field is nullable
    #on_delete=models.PROTECT prevents the deletion


#one to many
class Address2(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    Customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    zipField = models.CharField(max_length=255)
    #foreign keys are the primary keys of a class
    #django will create the primary key for Address2 class
    #multiple Address2 can be linked to one customer

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    # default=, when a cart object is created, django 
    # automatically assigns the id field, UUID 
    # default=uuid4, i'm not calling the uuid4 mtd i.e uuid4()
    # instead i'm passing a reference to it
    # if i call the mtd, at the time we create a migration,
    # a uuid will be generated and hard coded into our migration file
    # and we don't wnt to use the same value as our id
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    #on_delete=models.CASCADE, when a cart or product is deleted, all the associated items in the cart will be deleted
    quantity = models.PositiveSmallIntegerField()

    # to have a single instance of a product, we use a unique constraint
    # to ensure there are no dublicate records for the same product, in the same cart 
    # so if the customer has the same prduct of same cart, instead of increasing
    # the records, we'll just increase the quantity
    # we use the Meta class for this
    class Meta:
        unique_together = [['cart', 'product']]
        # a list of lists([[]]) cus we can have multiple unique constraints on different fields
        # for example[['cart', 'product'], []]



class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    # if delete a product all it's reviews will be deleted
    name = models.CharField(max_length=255)
    description = models.TextField()
    # the actual review
    date = models.DateField(auto_now_add=True)
    # when we create a review object this field gets automatically populated


    # a group is a collection of permissions
    # every time we create or update our models and migrate, django creates
    # permissions for us

    # content_type specifies all models in our app