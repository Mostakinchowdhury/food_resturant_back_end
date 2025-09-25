from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # শুধু GET, HEAD, OPTIONS = সবাই করতে পারবে
        if request.method in permissions.SAFE_METHODS:
            return True
        # শুধু admin হলে create/update/delete করতে পারবে
        return request.user and request.user.is_staff
class onlygetandcreate(permissions.BasePermission):
    def has_permission(self, request, view):
        # শুধু GET, HEAD, OPTIONS = সবাই করতে পারবে
        if request.method in ['GET','POST']:
          return True
        return  False

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
      # শুধু GET, HEAD, OPTIONS = সবাই করতে পারবে
        if request.method in permissions.SAFE_METHODS:
            return True
      # শুধু owner হলে update/delete করতে পারবে
        return obj.user == request.user

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
class IsadressOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.profile.user == request.user
