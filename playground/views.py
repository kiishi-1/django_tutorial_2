from django.forms import DecimalField
from django.shortcuts import render
from django.db import transaction, connection
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Value, Func, ExpressionWrapper
from django.db.models.functions import Concat
from django.db.models.aggregates import Count, Max, Min, Avg, Sum   
from django.contrib.contenttypes.models import ContentType
from store.models import Collection, Product, OrderItem, Order, Customer
from tags.models import TaggedItem


#a view fn is fn that takes a request and returns a response
# in other words, a request handler(in other frame works, action)


#Q is short for query
def say_hello1(request):
    #query_set = Product.objects.all()
    #every model in django as an attribute called objects
    #objects in Product.objects returns a manager object which
    #is an interface to the DB
    #like a remote control with a alot of buttons we an use to talk to our DB
    # the manager return a bunch of mtds (like all(), filter(), get()) that can be used to query or update data
    #there are other mtds the return results immediately like count() which returns
    # the number of records in a table 
    #Product.objects.all() is used for pulling out all the object in the Product table
    #Product.objects.get() for getting a single object
    #Product.objects.filter() for filtering data
    #most of this mtds return a query_set like the all()
    # query_set = Product.objects.all()
    #a query_set is an object that encapsulate a query
    # for product in query_set:
    #     print(product)
    #a scenario where a query set is evaluated is when we iterate over it

    #another scenario is when we convert it to a list
    #list(query_set)
    #another is when we access an individual element
    #query_set[0]
    #picking the first 5 element using a slicer ":"
    #query_set[0:5]

    #query sets are lazy cus they are evaluted at a later point
    #unlike methods that return a value immediately like count()
    #which return an integer value it there nothing extra to do with it
    #we're not going to apply a filter to it, or sort the result or build a
    #complex query around it

    #query_set.filter()
    #to filter the result and this will return a new query set

    #query_set.filter().filter().order_by()
    #we can call the filter mtd to filter the query set again
    #and the order_by mtd to sort the result

    #mtds for retrieving objects 
    #query_set = Product.objects.all()
    try:
        print("la")
        product = Product.objects.get(pk=1)
        print(product)
        print("lala")
    #get doesn't return a query set
    #retrieving a single object with id = 1
    #pk parameter is used to represent the primary key regard of the fields name
    #product = Product.objects.get(pk=0)
    # if the primary key doesn't have an attribute of 0 
    #it'll throw an exception (ObjectDoesNotExist) that it doesn't exist 
    except ObjectDoesNotExist:
        pass

    #another way
    print("first")
    query_set2 = Product.objects.filter().first()
    print(query_set2)
    print("first2")
    #we're calling the first() mtd of the query set
    #if the query set is empty the first() mtd will return none

    print("exist")
    exists = Product.objects.filter(pk=1).exists()
    print(exists)
    print("exist2")
    #checking if an object exist. it returns a boolean value

    #to get all the products that are 20 dollars
    query_set3 = Product.objects.filter(unit_price=20)

    #to get all the products that are more expensive(greater than) the 20 dollars
    query_set4 = Product.objects.filter(unit_price__gt=20)
    query_set5 = Product.objects.filter(unit_price__range=(20, 30))
    #unit_price__gt unit_price greater than(>)
    #unit_price__lt unit_price less than(<)
    #unit_price__range within range (lowest, highest)
    #we are these as the keys
    #check Query Set Api, field look up

    #to filter  relationship across tables
    query_set6 = Product.objects.filter(collection__id__range=(1, 2, 3))
    #__ is used to navigate the relationship
    #collection__id__range(1, 2, 3) is going into the collection table accessing the id column
    #and selecting the products in indexes 1, 2, 3 only 
    query_set7 = Product.objects.filter(title__icontains='coffee')
    #title__contains='coffee' accessing the title field in the Product table
    #and selecting for the product that contain coffee in the title field
    #contains is case sensitive
    #icontains isn't
    #there's also startwith, endswith and they're case insensitive variation

    #using date
    query_set8 = Product.objects.filter(last_update__year=2021)
    #last_update__date can also be used

    query_set9 = Product.objects.filter(description__isnull=True)
    # we won't get anything because all our product have description

    #products: inventory < 10 AND price < 20
    #performing AND operation
    query_set10 = Product.objects.filter(inventory__lt=10, unit_price__lt=20)
    query_set11 = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20)

    #for OR operator
    query_set12 = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20))
    #the Q object encapsulate a keyword argument(parameter) or query expression

    #AND not the only way or the best way 
    query_set13 = Product.objects.filter(Q(inventory__lt=10) & Q(unit_price__lt=20))

    #NOT operator
    #~Q(unit_price__lt=20)) is the inverse of Q(unit_price__lt=20))
    query_set14 = Product.objects.filter(Q(inventory__lt=10) & ~Q(unit_price__lt=20))

    #sometimes when filtering data we need to reference a particular field
    #products: inventory = price
    #we use the F class(object) to reference a particular field
    query_set15 = Product.objects.filter(inventory=F('unit_price'))

    #we can also reference a field in a related table
    query_set16 = Product.objects.filter(inventory=F('collection__id'))
    #comparing the inventory field with the collection_id field in 
    # the product table since collection_id field represent the id
    #  of collections in the collection table

    #sorting data
    query_set17 = Product.objects.order_by('title')
    #sorting the products by they're title, in ascending order
    #for descending order, -title

    query_set18 = Product.objects.order_by('unit_price', '-title')
    #the products will be sorted using their unit price and then by their title(in descending order)
    query_set19 = Product.objects.order_by('unit_price', '-title').reverse()
    #the products will be sorted in reverse i.e, using unit price in descending order
    # and then by their title in ascending order

    query_set20 = Product.objects.filter(collection__id=1).order_by('unit_price')
    #checking if any product has 1 in the collection_id field of the product table and then sort the
    #products by their unit price
    # OR
    #merging the id field in the collection table with the collection_id field of the product table
    #and then using that id in the collection table to get 
    # products with the same id in the collection_id field of the product table

    query_set21 = Product.objects.filter(collection__title="pets").order_by('unit_price')
    #merging the id field in the collection table with the collection_id field of the product table
    #and then using the id of the record that has the collection "pets" title in the collection table to get 
    # products with the same id in the collection_id field of the product table

    prod = Product.objects.order_by('unit_price')[0]
    #OR
    prod2 = Product.objects.earliest('unit_price')
    # sorting the products by their unit price and picking the first item(element)

    prod3 = Product.objects.latest('unit_price')
    #sorting the products by their unit price in descending order and picking the first item(element)

    #limiting results
    query_set22 = Product.objects.all()[:5]
    #to show 5 items per page
    #[:] for array slicing
    #[:5] returns the first 5 items(objects) i.e at indexes 0, 1, 2, 3, 4

    #to get the products on the second page
    query_set23 = Product.objects.all()[5:10]
    # it'll skip the first 5 and get the second 5 products(items) 
    #i.e at indexes 5, 6, 7, 8, 9

    #to select fields to query
    
    query_set24 = Product.objects.values("id", "title", "collection__title")
    #getting the values in the id and title column
    #"collection__title" is to get the items in title field(column) in the collection table
    #merging the id field in the collection table with the collection_id field of the product table
    #and then using that id in the collection table to as reference to get the titles 
    #in the collection table whose id are in the collection_id field in the product table
    #we are getting the titles in the collection table according to their id
    #on the collection_id field in the product table

    #we are actually getting a dictionary(map) object
    #{'id': 2, 'title': 'Island Oasis - Raspberry', 'collection__title': 'Beauty'}
    #{'id': 3, 'title': 'Shrimp - 21/25, Peel And Deviened', 'collection__title': 'Beauty'}
    #{'id': 7, 'title': 'Turkey Tenderloin Frozen', 'collection__title': 'Cleaning'}
    # {'id': 14, 'title': 'Tofu - Soft', 'collection__title': 'Cleaning'}

    #with values_list
    query_set25 = Product.objects.values_list("id", "title", "collection__title")
    #we get a bunch of tuples instead of dictionaries
    #(2, 'Island Oasis - Raspberry', 'Beauty')
    # (3, 'Shrimp - 21/25, Peel And Deviened', 'Beauty')
    #(7, 'Turkey Tenderloin Frozen', 'Cleaning')
    # (14, 'Tofu - Soft', 'Cleaning')

    #to get the product ordered
    query_set28 = OrderItem.objects.values("product__id", "product__title").distinct()
    #.distinct() is used to get ride of duplicate

    #to select all product with the id's gotten
    query_set29 = Product.objects.filter(id__in=OrderItem.objects.values("product__id").distinct()).order_by('title')

    #to select fields to query2
    query_set30 = Product.objects.only("id", "title")

    #note: with the only method we get instances of the Product class while with the values method we get 
    #dictionary objects
    #careful how you use the only mtd cus it might make queries under the hood
    #you are not aware of which will affect performance

    #defer
    query_set31 = Product.objects.defer()
    # the differ mtd does the opposite of the only mtd
    #with this mtd we can defer the loading of certain fields to later

    #selecting related objects
    query_set32 = Product.objects.select_related('collection').all()
    #we want to preload the products with our collection
    #we select the field we want to preload select_related('collection')
    #we used select_related cus when the other end of the relationship has one instance 
    # Product has one collection i.e product has one instance
    # one to one

    #we use pre_fetch_related when the other end of the relationship has many objects(instance)
    #e.g promotions
    # essentially, a Product can have one collection but many promotions
    # one to many
    query_set33 = Product.objects.prefetch_related('promotions').all()


    query_set34 = Product.objects.prefetch_related('promotions').select_related('collection').all()

    #get the last 5 orders with their customers and item including products
    query_set35 = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
    #customer field is pre loaded. select_related cus an order can only have 1 customer(i.e one instance)
    # one to one
    #while we are set to get the first 5 orders but we want to get the last 5 orders
    # so the orders are ordered by placed at and they are set in descending order 
    #in the Order class there's no order item field 
    #but in the the OrderItem class we have the order field which is a foreign key to Order class
    #so django will create a reverse relationship with the Order class
    #the name of the relationship will be orderitem_set. this is the convention
    #django uses to create reverse relationship
    #if we don't like it we can set it using the related_name parameter(argument)
    #we use the default
    #it represent the target class, OrderItem
    # prefetch_related('orderitem_set') cus an order can only have multiple items(i.e multiple instance)
    # one to many
    #orderitem_set__product cus want to span the relationship and access the product field

    #aggregating objects
    #to count
    result = Product.objects.aggregate(count=Count('id'), min_price=Min("unit_price"))
    #we specify the field we want to use to count in the Count object(Count())
    #it's idle to use the primary key

    query_set35 = Product.objects.filter(collection__id=1).aggregate(count=Count('id'), min_price=Min("unit_price"))

    #annotation
    #to add additional attributes(field) to our objects while querying them
    query_set36 = Customer.objects.annotate(isnew=Value(True))
    #if we want to give each customer a custom field
    # isnew=True will fail, we have to wrap inside an expression(Value())

    query_set37 = Customer.objects.annotate(new_id=F("id"))
    #here we are creating a new field and assigning the values of the id(primary key) to it

    #we can also perform computation
    query_set38 = Customer.objects.annotate(new_id=F("id") + 1)
    #we are adding 1 to each id
    query_set39 = Customer.objects.annotate(
        #calling CONCAT fn
        full_name=Func(F('first_name'), Value(' '), F('last_name'), function='CONCAT')
    )
    #Func() object is used when we want to perform a function, (duh)
    #creating a new field full_name and assigning values which  are
    # concatination(joining) of the values of the first_name and last_name fields
    #using the CONCAT function (function='CONCAT')
    #Value(' ') passing space in between first_name and last_name
    #using Value(' ') instead of ' ' directly cus we it will fail(django will think it's a field).
    # we have to pass it inside an expression

    #short hand
    query_set40 = Customer.objects.annotate(
        #calling CONCAT fn
        full_name=Concat('first_name', Value(' '), 'last_name')
    )

    #to see the orders each customer has placed
    query_set41 = Customer.objects.annotate(
        orders_count=Count('order')
    )
    #we are creating a new field "orders_count" in the Customer table and
    #assigning the number of orders each customer made. so the count function
    #is counting the order of each customer
    #merging the id field in the Customer table with the Customer_id field of the Order table
    #and then using that id in the Customer table to get the
    # orders(the rows, i guess) with the same id in the Customer_id field of the Order table 
    #we don't have a order field in the Customer class so we are going to use
    #the reverse relationship. the name of the relationship is supposed to be 
    #order_set but for reason we can't use order_set in django, it'll throw an exception
    #we'll use order instead, which was suggested in the exception

    #working with Expression Wrappers
    #we use this class when building with complex expressions
    discounted_price = ExpressionWrapper(F("unit_price") * 0.8, output_field=DecimalField( ))
    query_set42 = Product.objects.annotate(
        discounted_price=discounted_price
    )
    #using this discounted_price=F("unit_price") * 0.8 we get an expression
    #Expression contains mixed types: DecimalField (unit_price), FloatField(0.8)
    #we must set the output field to solve the problem, for monetary values DecimalField
    # must be used cus FloatField have a rounding issue and are not really accurate.
    # First import the Expression Wrappers class
    
    
    content_type = ContentType.objects.get_for_model(Product)
    #ContentType is a model hence why it has the objects attributes
    #get_for_model is a special mtd only available in the objects manager(ContentType.objects)
    #objects returns a manager object which is an interface or a gateway to the DB
    #like a remote control with a alot of buttons we an use to talk to our DB
    # the manager return a bunch of mtds (like all(), filter(), get()) that can be used to query or update data
    #getting the content type id for the Product Model
    #content_type represent the product row in the content type table
    #it is how we can find the content type id for the Product model
    #do not rely on the content type id(e.g for Product) cus the content type id in
    # the development Db can be different from the content type id in production DB

    # we can use it to filer the TaggedItem
    TaggedItem.objects.filter(
        content_type=content_type,
        object_id=1
    )
    #TaggedItem.objects.filter(content_type=content_type,object_id=1) will return a
    #bunch of TaggedItem objects 
    # we giving it two filters, content_type i.e of Product class(which has the content type id of Product class) and object_id
    #if the content type of the Product class is available in the content_type field of the TaggedItem Table
    #object_id is the id of the product whose tags you want to query
    #i thick we are getting all products in the product table and the selecting
    #the product at index 1 and getting the tags of that product
    #the actual tag is not stored in the TaggedItem table, only the tag id
    #is stored as a foreign key
    
    query_set43 = TaggedItem.objects \
        .select_related('tag') \
            .filter(
                content_type=content_type,
                object_id=1
            )
    #we want to preload the tag field(all the data in the tag table)
    #so we don't have extra queries to the database that incresing loading duration
    #we select the field we want to preload select_related('tag')
    #we used select_related cus when the other end of the relationship has one instance 
    # TaggedItem has one Tag i.e TaggedItem has one instance
    # one to one
    #getting the tags where `tags_taggeditem`.`content_type_id` = 11 AND `tags_taggeditem`.`object_id` = 1

    # using custom managers
    TaggedItem.objects.get_tags_for(Product, 1)

    query_set44 = Product.objects.all()
    list(query_set44)
    #when we convert query_set44 to a list django will evalute the query set
    #and the go to the DB to get the result
    # django will store the result somewhere in memory called the query cache
    # caching only happens when we evalute the entire query set first
    #e.g
    # list(query_set44)
    # query_set44[0] 
    #this will only have one query and the get the first item from the cached query set

    # query_set44[0] 
    # list(query_set44)
    #this will have two queries cus we are not evaluating the entire query set first


    #inserting a record(row) into DB
    # collection = Collection()
    # collection.title = 'video games'
    # collection.featured_product = Product(pk=1)
    # collection.featured_product = Product(id=1)
    #passing the product in id = 1(primary key)
    #can also do this
    # collection.featured_product_id = 1

    # collection = Collection(title='video games')
    #no intellisense and keywords(parameter names) don't get updated
    # collection.save()
    #or
    #short hand
    # collection = Collection.objects.create(title='video games', featured_product_id=1)
    #no intellisense and keywords(parameter names) don't get updated
    # the parent record should exist before we can created the child record
    #this is how relational DB works
    #Product was created before Collection

    #updating 
    # collection2 = Collection(pk=11)
    # #pk=11 is the id of our new collection(record) of title 'video games'
    # collection2.title = 'games'
    # collection2.featured_product = None
    # collection2.save()

    #OR
    collection2 = Collection.objects.get(pk=11)
    #we first read(get) the record so we have all the values in memory
    # to properly update the record
    collection2.featured_product = None
    collection2.save()

    #OR
    # collection2 = Collection.objects.filter(pk=11).update(featured_product=None)

    #deleting objects
    # collection2.delete()

    #deleting multiple objects
    # collection2.objects.filter(id__gt=5).delete()

    # to make multiple changes to our DB in an atomic way
    # meaning all changes should be saved together or if one of the changes fail
    # then all changes should be rolled back
    # saving an order with it's items

    # to have control over what parts of your view function has used the transaction
    # we use transaction.atomic() as a context manager 

    # ...
    with transaction.atomic():
        order = Order()
        order.customer_id = 1
        # order.customer = 1 same thing
        order.save()
        # we should always create the parent record before creating the child record
        item = OrderItem()
        item.order = order
        item.product_id = 1
        item.quantity = 1
        item.unit_price = 10
        item.save()

        # an exception(Inconsistent State) will be thrown when saved
        # so we'll have an order without an item
        # to solve this we'll wrap both operations in a transaction
        # so either both of them will be commited together or if one fail, then both 
        # changes will be rolled back
    
    query_set45 = Product.objects.raw('SELECT * FROM store_product')
    # every manager has the raw mtd for executing SQL queries
    # Product.objects.raw('SELECT * FROM store_product') will return a queryset 
    # but it's different from the query set we've been getting
    # we will not have the special mtds like annotate or filter 

    query_set46 = Product.objects.raw('SELECT id, title FROM store_product')

    # to execute queries that do not ma to the model in those cases we can access the
    # DB directly and by pass the model layer 
    cursor = connection.cursor()
    cursor.execute('')
    # cursor.execute(''), here we can pass any SQL statemnet no limitations
    cursor.close()
    # after executing our query we should always close the cursor to release the allocator resourses

    with connection.cursor() as cursor2:
        cursor.execute()
    
    # the cursor is always going to get closed even with an exception

    with connection.cursor() as cursor3:
        cursor.callproc('get_customers', [1, 2, 'a'])
    # cursor.callproc() is used to execute store procedures
    #cursor.callproc('get_customers', [1, 2, 'a']) call a stored procedure get_customers
    # and giving it a bunch of parameters [1, 2, 'a']

    return render(request, 'hello.html', {'name': 'Mosh', 'result': list(query_set45)})

@transaction.atomic()
# @transaction.atomic() is used as decorator
# it will wrap the entire say_hello2 view function into a transaction
# so all the code here will run inside a transaction
#transaction.atomic can be used as a decorator or context manager
def say_hello2(request):
    order = Order()
    order.customer_id = 1
    # order.customer = 1 same thing
    order.save()
    # we should always create the parent record before creating the child record
    item = OrderItem()
    item.order = order
    item.product_id = 1
    item.quantity = 1
    item.unit_price = 10
    item.save()

    # an exception(Inconsistent State) will be thrown when saved
    # so we'll have an order without an item
    # to solve this we'll wrap both operations in a transaction
    # so either both of them will be commited together or if one fail, then both 
    # changes will be rolled back

    return render(request, 'hello.html', {'name': 'Mosh'})

def say_hello(request):
    return render(request, 'hello.html', {'name': 'Mosh'})
