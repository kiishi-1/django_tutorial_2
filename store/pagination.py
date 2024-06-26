from rest_framework.pagination import PageNumberPagination

# to resolve this pagiantion warning
# WARNINGS:
# ?: (rest_framework.W001) You have specified a default PAGE_SIZE pagination
# rest_framework setting, without specifying also a DEFAULT_PAGINATION_CLASS.
# HINT: The default for DEFAULT_PAGINATION_CLASS is None. 
# In previous versions this was PageNumberPagination.
# If you wish to define PAGE_SIZE globally whilst defining pagination_class 
# on a per-view basis you may silence this check.

class DefaultPagination(PageNumberPagination):
    page_size = 10