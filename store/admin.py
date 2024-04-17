from typing import Any
from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models.query import QuerySet
from django.db.models.aggregates import Count
from django.http.request import HttpRequest
from django.utils.html import format_html, urlencode
from django.urls import reverse

from tags.models import TaggedItem
from . import models
# . means current folder(in this case app)
# so we are importing the models in this app

class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    # title will be in the filter section
    parameter_name = 'inventory'
    # parameter_name will be used in the query string

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            ('<10', 'Low')
        ]
    #an inbuilt attribute(mtd) specifies what items will appear in the filter section
    # that is, one of the filter options
    # 'Low' is what will be shown on the filter section
    # '<10' will be used for operations in the class

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any]:
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
    #an inbuilt attribute(mtd) where will implement the filtering logic
    # inventory__lt=10 means if the inventory in the Product table is less than 10
    # you when you click on Low, it will get you the product with inventory status of Low
    # cus the ProductAmin class as a mtd called inventory_status that also checks
    # if the inventory is less than 10

class TagInline(GenericTabularInline):
    # we use GenericTabularInline with generic objects
    # using inlines we can manage the tag in the Product page(form)
    autocomplete_fields = ['tag']
    model = TaggedItem


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    # editing forms
    # fields = ['title', 'slug']
    # exclude = ['promotions']
    # readonly_fields = ['title']
    autocomplete_fields= ['collection']
    search_fields = ['title']
    prepopulated_fields = {
        'slug': ['title']
    }
    actions = ['clear_inventory']
    inlines = [TagInline]
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    # using @admin.register(models.Product) as a decorator
    # of the ProductAdmin class instead of 
    # manually registering like this admin.site.register(models.Product, ProductAdmin)

    # ['title', 'unit_price', 'inventory_status', 'collection']
    # collection is a related field hence, django will show a string representation of a collection
    # recall that we overode the __str__ mtd of the collection class
    # so when showing the so when showing the product, for each product 
    # django will run the __str__ mtd to get the title of that collection of that product
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 10
    list_select_related = ['collection']
    # to preload the collection

    #  to show a particular field in the collection model
    def collection_title(self, product):
        return product.collection.title
        # we are using product the instance of the Product class and accessing the
        # collection table via the collection_id field in the Product table
        #to get the values in the title field

    # django doesn't know how to solve the content of inventory status column
    # to implement sorting we need to apply @admin.display
    # ordering is the field used for sorting the data in the column
    #and we use inventory(a field in the Product model) as the order
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:  
            return 'Low'
        return 'OK'
    # self is the instance of the class it's in.
    # It allows you to refer to the instance variables and methods within the class
    # product represents an instance of the Product model

    @admin.action(description='Clear Inventory')
    # @admin.action(description='Clear Inventory') is used to give the text 
    # we'll use as description in the actions drop down
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated.',
            messages.ERROR
            # messages.ERROR to show error style messages
        )
        # every model admin has the mtd for showing a message to the  user

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_count']
    search_fields=['title']

    @admin.display(ordering='product_count')
    def product_count(self, collection):
        # return collection.product_count

        # instead of hard coding the link cus it can change any time
        # we use this format admin:app_model_page
        # app is the app we are working with at the moment, store
        # model is the target model, product
        # page is the target page, changelist
        url = (
            reverse('admin:store_product_changelist') 
            + '?'
            + urlencode({
                'collection__id': str(collection.id)
            }))
        # ? marks the beginning of a query string
        # ?collection__id=3 = urlencode({'collection__id': str(collection.id)}))
        # and it means find the products(row) with collection id 3 in the product class(table)
        # hence http://127.0.0.1:8000/admin/store/product/?collection__id=3 means go to
        # product page, get the products(row) with collection id 3

        return format_html('<a href="{}">{}</a>', url, collection.product_count)
    # product_count field originally doesn't exist on the collection table
    # so will override the query set and annotate the collections with the number of products

    # overriding the base queryset(in this case, collection)
    # from admin.ModelAdmin we get
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            product_count=Count('products')
        )
    #annotation
    #to add additional attributes(field) to our objects while querying them


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name',  'membership', 'orders']
    # we won't be able to use 'first_name', 'last_name' in our list_display
    # cus we tied the customer model with the user model
    # to fix this we'll define a mtd called first_name in the customer model
    # and we'll return user.first_name in that mtd. we'll do this for last_name too
    list_editable = ['membership']
    list_per_page = 10
    # ordering = ['first_name', 'last_name']
    list_select_related = ['user']
    # when getting customers we want to also preload the users otherwise
    # for each customer, separate query will be sent to the DB
    ordering = ['user__first_name', 'user__last_name']
    # 'user__first_name', 'user__last_name' cus we're getting from the user model
    # when loading customer we want to preload them otherwise for each customer a query will be sent to the DB
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='orders_count')
    def orders(self, customer):
        url = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            }))
        return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
        )


class OrderItemInline(admin.TabularInline):
    # admin.TabularInline gives you a layout in the form of row and columns
    # admin.StackedInline gives you a layout in the form a normal form
    # OrderItemInline indirectly inherits from admin.ModelAdmin so it ashould have all 
    # the attributes the OrderAdmin has
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    extra = 0
    # extra = 0 if you don't want the default placeholders
    model = models.OrderItem
    

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields= ['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer']
