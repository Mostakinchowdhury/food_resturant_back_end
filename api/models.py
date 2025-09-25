from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .manager import myUserManager,CartitemManager
from django.contrib.auth import get_user_model
import uuid
from os.path import join,splitext
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import PermissionsMixin

User=settings.AUTH_USER_MODEL
GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others'),
    )

# custom user model
class CustomUser(AbstractBaseUser,PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    USERNAME_FIELD="email"
    EMAIL_FIELD="email"
    REQUIRED_FIELDS=["first_name","last_name"]
    objects=myUserManager()
    def __str__(self):
       return self.email

# profile pic upload path
def genaretprofilepath(instance,filename):
    today=datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")
    extension_name=splitext(filename)[1] # Get the file extension
    # Generate a unique filename using UUID
    uniqe_filename = f"{uuid.uuid4().hex}{extension_name}" # Generate a UUID and convert to string
    return join("profiles",year,month,day,uniqe_filename)


# custom profile model
class Profile(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name='profile',related_query_name='profile')
    phone_num=models.CharField(max_length=20,null=True,blank=True)
    country=models.CharField(max_length=100,default='United kingdom')
    bio=models.TextField(max_length=320,null=True,blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    birth_date=models.DateField(null=True,blank=True)
    profile_image=models.ImageField(upload_to=genaretprofilepath,blank=True,null=True)
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s Profile"


# custom setting model
class Setting(models.Model):
  user=models.OneToOneField(CustomUser,related_name="setting",related_query_name="setting",on_delete=models.CASCADE)
  theme=models.CharField(max_length=100,default='light')
  language=models.CharField(max_length=200,default='English')
  setting_adding_time=models.DateTimeField(auto_now_add=True)
  setting_update_time=models.DateTimeField(auto_now=True)
  def __str__(self):
        return f"Setting for {self.user.first_name} {self.user.last_name}"


# custom tag model
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    tag_author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tags", related_query_name="tags", null=True, blank=True,default="admin")
    def __str__(self):
        return self.name


# genaret uniqe category image path
def genaretcategorypath(instance,filename):
    today=datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")
    extension_name=splitext(filename)[1] # Get the file extension
    # Generate a unique filename using UUID
    uniqe_filename = f"{uuid.uuid4().hex}{extension_name}" # Generate a UUID and convert to string
    return join("categories",year,month,day,uniqe_filename)
#product category model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=genaretcategorypath, blank=True, null=True)
    def __str__(self):
        return self.name


# genaret uniqe product image path

def genaretproductpath(instance,filename):
    today=datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")
    extension_name=splitext(filename)[1] # Get the file extension
    # Generate a unique filename using UUID
    uniqe_filename = f"{uuid.uuid4().hex}{extension_name}" # Generate a UUID and convert to string
    return join("products",year,month,day,uniqe_filename)

def genaretorderpath(instance,filename):
    today=datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")
    extension_name=splitext(filename)[1] # Get the file extension
    # Generate a unique filename using UUID
    uniqe_filename = f"{uuid.uuid4().hex}{extension_name}" # Generate a UUID and convert to string
    return join("paymend_prove",year,month,day,uniqe_filename)

# custom product model
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products",related_query_name="products")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)  # 999999.99 পর্যন্ত
    max_price = models.DecimalField(max_digits=8, decimal_places=2,null=True,blank=True)  # 999999.99 পর্যন্ত
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=genaretproductpath, blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name="products", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return 0
    @property
    def review_count(self):
        reviews = self.reviews.all()
        return reviews.count()
    # count total how much ar added to cart
    @property
    def addedtocard(self):
        tacs=self.cartitem.all()
        if not tacs.exists():
            return 0
        return sum(tac.quantity for tac in tacs)
    def save(self, *args, **kwargs):
        if self.max_price is None:
            self.max_price = self.price
        super().save(*args, **kwargs)
# custom cart model
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart",related_query_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.email}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.checked_items())

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())
# custom cart item model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name="cartitem",related_query_name="cartitem")
    quantity = models.PositiveIntegerField(default=1)
    ischeaked=models.BooleanField(default=False)
    added_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects=CartitemManager()

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity

# custom order model
class Order(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PAIDANDPROCESSING", "Paid and Processing"),
        ("CASHANDPROCESSING", "Cashon and Processing"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
        )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders",related_query_name="orders")
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name="order",related_query_name='order')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    is_cashon = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default="GBP")
    orderitems_string=models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Order {self.id} - {self.user.first_name} {self.user.last_name} ({self.status})"

    @property
    def total_amount(self):
        return self.cart.total_price

# custom product revew model
class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews",related_query_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews",related_query_name="reviews")
    rating = models.PositiveIntegerField()  # 1 থেকে 5 পর্যন্ত
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.first_name} {self.user.last_name} for {self.product.name}"


class subscribers(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

from django.core.exceptions import ValidationError

class Address(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="addresses")
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.profile.addresses.count() >= 3 and not self.pk:
            raise ValidationError("Sorry, you are not allowed to add more than 3 addresses")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Address for {self.profile.user.first_name} {self.profile.user.last_name}"






# coupeon/promo code model

from django.db import models
from django.utils import timezone

from django.utils import timezone
from django.db import models

class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)   # যেমন SAVE10, FIRST50
    discount_percent = models.PositiveIntegerField(default=0)  # % discount
    max_uses = models.PositiveIntegerField(default=1)  # কয়বার ব্যবহার করা যাবে (999 মানে unlimited)
    used_count = models.PositiveIntegerField(default=0)  # কয়বার ব্যবহার হয়েছে
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    max_uses_per_user = models.PositiveIntegerField(default=1)  # প্রতি user এর limit

    def is_valid(self):
        current_time = timezone.now()

        # active check
        if not self.active:
            return False

        # valid_from check
        if self.valid_from > current_time:
            return False

        # valid_to skip check
        if self.valid_to and current_time > self.valid_to:
            return False

        # max_uses skip check
        if self.max_uses != 999 and self.used_count >= self.max_uses:
            return False

        return True

    def __str__(self):
        return f"{self.code} ({'Unlimited' if self.max_uses == 999 else f'{self.used_count}/{self.max_uses}'})"


    def __str__(self):
        return self.code

# PromoUsage   models

class PromoUsage(models.Model):
    """ কে কোন coupon কতবার ব্যবহার করেছে সেটা track করবে """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="promo_usages")
    promo = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name="usages")
    used_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'promo')

    def __str__(self):
        return f"{self.user.email} - {self.promo.code} ({self.used_count} times)"
