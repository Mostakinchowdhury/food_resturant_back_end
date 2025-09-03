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
    address=models.CharField(max_length=255)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    zip_code=models.CharField(max_length=20)
    phone_num=models.CharField(max_length=20)
    country=models.CharField(max_length=100)
    bio=models.TextField(max_length=320)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    birth_date=models.DateField(null=True,blank=True)
    profile_image=models.ImageField(upload_to=genaretprofilepath,blank=True,null=True,default="profiles/default.png")
    def __str__(self):
        return f"{self.user.username}'s Profile"


# custom setting model
class Setting(models.Model):
  user=models.OneToOneField(CustomUser,related_name="setting",related_query_name="setting",on_delete=models.CASCADE)
  theme=models.CharField(max_length=100)
  language=models.CharField(max_length=200)
  setting_adding_time=models.DateTimeField(auto_now_add=True)
  setting_update_time=models.DateTimeField(auto_now=True)
  def __str__(self):
        return f"Setting for {self.user.username}"


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

# custom product model
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products",related_query_name="products")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)  # 999999.99 পর্যন্ত
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=genaretproductpath, blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name="products", blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
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
# custom cart model
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart",related_query_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.checked_items())


# custom cart item model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
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
        ("PROCESSING", "Processing"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
        )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders",related_query_name="orders")
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE,related_name="order",related_query_name='order')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username} ({self.status})"

    @property
    def total_amount(self):
        return self.cart.total_price
    @property
    def orderitems_string(self):
        return ",".join(f"{item.product.name} x {item.quantity}" for item in self.cart.items.checked_items())

# custom product revew model
class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews",related_query_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews",related_query_name="reviews")
    rating = models.PositiveIntegerField()  # 1 থেকে 5 পর্যন্ত
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

