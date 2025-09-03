from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Manager
# custom manager for cartitem,cart model include get_create method

# import base manager


class myUserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_field):
        if not email:
            raise ValueError("Email is a requred field")
        email=self.normalize_email(email)
        user=self.model(email=email,password=password,**extra_field)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,email,password=None,**extra_field):
        extra_field.setdefault("is_superuser",True)
        extra_field.setdefault("is_staff",True)
        extra_field.setdefault("is_active",True)
        extra_field.setdefault("is_verified",True)
        return self.create_user(email,password,**extra_field)

    def active_user(self):
        return self.get_queryset().filter(is_active=True)


# create custom manager for cart and cartitem model
class CartitemManager(Manager):
    def checked_items(self):
        return self.get_queryset().filter(ischeaked=True)
