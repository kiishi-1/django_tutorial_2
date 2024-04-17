from rest_framework import permissions
# from rest_framework.permissions import IsAuthenticated, BasePermission
# NB:BasePermission is the base class for all permissions in django rest framework
# classes like IsAuthenticated class extends BasePermission.

# we'll apply this in our product view set
class IsAdminOrReadOnly(permissions.BasePermission):
    # we override has_permission
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            # permissions.SAFE_METHODS are your GET, HEAD and OPTIONS
            return True
            # any one can access the target view
        return bool(request.user and request.user.is_staff)
        # return true if both conditions(request.user - user is logged in, request.user.is_staff - user is an admin) 
        # in the bool mtd are true else return false
        

class FullDjangoModelPermissions(permissions.DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        # this is the mapping of http mtds(self.perms_map['GET']) 
        # and relevant permissions(['%(app_label)s.view_%(model_name)s'])
        # ['%(app_label)s.view_%(model_name)s'] represent the codename format for permissions
        # check permissions table in DB
        # the mapping as already been done for other http mtd like(POST, PUT, PATCH and DELETE)
        # check permissions.DjangoModelPermissions
        # to send a GET request the user should have a view permission
        # we'll use this permission in our customer view set
        # we don't want to pervent users outside the customer services group from viewing data
        
class ViewCustomerHistoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('store.view_history')
        # if this returns true the user will have permission and
        # will be able to access the history