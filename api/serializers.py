from .models import Profile, Setting, Tag, Order, Product, Category, Cart, CartItem, ProductReview, Address, PromoUsage
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from .utils import password_reset_email


def get_tokens_for_user(user):
    if not user.is_active:
      raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

User = get_user_model()


# serializer for profile model

# subscriber serializer
from  .models import subscribers

class subscribersserializer(serializers.ModelSerializer):
    class Meta:
        model = subscribers
        fields = ['id', 'email', 'created_at']
        extra_kwargs = {
            'email': {'required': True},
        }
        read_only_fields = ['created_at']

# adresses serializer

class adressserializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city','country', 'created_at','profile']
        read_only_fields = ['created_at']
        extra_kwargs = {
            'street': {'required': True},
            'city': {'required': True},
            'country': {'required': True},
        }

class ProfileSerializer(serializers.ModelSerializer):
    addresses=adressserializer(many=True,read_only=True)
    id = serializers.IntegerField()
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ['user','id','addresses']

# serializer for setting model

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = "__all__"
        read_only_fields = ['user','id']

# serializer for tag model
class TagSerializer(serializers.ModelSerializer):
    tag_author = serializers.SlugRelatedField(slug_field="email", read_only=True)
    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ['tag_author','id']




#serializer for category model

# Product review serializer
class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)
    product = serializers.SlugRelatedField(slug_field="name", read_only=True)
    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at','updated_at']
        read_only_fields = ['id', 'product', 'user', 'created_at','updated_at']



# serializer for products image
from .models import Product_images,Supercategory
class ProductimgsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product_images
        fields="__all__"
        read_only_fields=['id',]

# serializer for product model
class ProductSerializer(serializers.ModelSerializer):
    category=serializers.SlugRelatedField(slug_field="name",read_only=True)
    tags=TagSerializer(many=True,read_only=True)
    productimgs=ProductimgsSerializer(many=True,read_only=True)
    reviews=ProductReviewSerializer(many=True,read_only=True)
    added_to_cart_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Product
        fields = ['id','category','name','description','price','max_price','stock','tags','created_at','update_at','reviews','average_rating','review_count','addedtocard','added_to_cart_count',"productimgs"]
        read_only_fields = ['id','category','create_at','update_at','tags','reviews','average_rating','review_count','addedtocard','added_to_cart_count']



# category serializer

class CategorySerializer(serializers.ModelSerializer):
    products=ProductSerializer(many=True,read_only=True)
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ['id','products']

# Supercategory serializer

class SupercategorySerializer(serializers.ModelSerializer):
    category=CategorySerializer(many=True,read_only=True)
    class Meta:
        model = Supercategory
        fields = "__all__"
        read_only_fields = ['id','category']


# serializer for order model
class OrderSerializer(serializers.ModelSerializer):
    user_email = serializers.SlugRelatedField(source="user", slug_field="email", read_only=True)
    class Meta:
        model = Order
        fields = [
            "id", "user", "user_email", "cart", "status",
            "address", "phone", "ordered_at",
            "total_amount", "orderitems_string","amount"
        ]
        read_only_fields = ['id','user','ordered_at','total_amount','orderitems_string']

    def create(self, validated_data):
      order = Order.objects.create(user=self.context['user'],**validated_data)
      return order



# CART ITEM SERIALIZER
class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source="product", read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id", "cart", "product", "product_detail",
            "quantity", "ischeaked", "added_at", "subtotal",
        ]
        read_only_fields = ["id", "added_at", "subtotal"]

# serializer for cart model
class CartSerializer(serializers.ModelSerializer):
    user_email = serializers.SlugRelatedField(source="user", slug_field="email", read_only=True)
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "user_email", "items", "created_at", "update_at", "total_price",'total_quantity']
        read_only_fields = ["id", "user", "created_at", "update_at", "total_price"]

    def create(self, validated_data):
        user = self.context["user"]
        return Cart.objects.create(user=user, **validated_data)



# user relatate serializers

# serializer for user registration
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name','password','password2','is_staff','is_superuser']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    def validate_password(self, value):
        if not value.strip():
            raise serializers.ValidationError("This field cannot be blank.")
        if len(value)<8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value.strip()
    def validate_password2(self, value):
        return value.strip()
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs


    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return "We sent an OTP to your email. Please check your inbox and verify your account."


# serializer for user login
class loginserializer(serializers.Serializer):
  password=serializers.CharField(min_length=8)
  email=serializers.EmailField()
  def validate(self, attrs):
     user=authenticate(email=attrs['email'],password=attrs['password'])
     if user is not None:
       if not user.is_verified:
            raise serializers.ValidationError("Email is not verified")
       attrs['token']=get_tokens_for_user(user)
     else:
       raise serializers.ValidationError("Your information not match with any record try again")
     return attrs


# password change serializer
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return value

    def validate(self, attrs):
        user = self.context.get('user')
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError("New password and confirm password do not match")

        if not user.check_password(old_password):
            raise serializers.ValidationError("Old password is incorrect")

        return attrs

    def save(self, **kwargs):
        user = self.context.get('user')
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user



from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from .utils import password_reset_email
class ResetPasswordgenaretSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist")
        return value
    def save(self, **kwargs):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        # Here you would typically send an email with a reset link or token
        # For simplicity, we'll just return the user object
        token = PasswordResetTokenGenerator().make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uidb64}/{token}/"
        send_mail(
                subject="Reset your password",
                message="Click the link to reset your password",
                html_message=password_reset_email(reset_link),
                from_email=f"OrderUK <{settings.EMAIL_HOST_USER}>",
                recipient_list=[email],
            )
        return "we have sent you a link to reset your password in your email account"


class setResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            if password != confirm_password:
                raise serializers.ValidationError({'confirm_password':"Password and confirm password do not match"})

            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("The reset link is invalid or has expired")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError:
            raise serializers.ValidationError("The reset link is invalid or has expired")
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")




# promo code / coupe on code serializer
from .models import PromoCode

class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'   # চাইলে নির্দিষ্ট ফিল্ড দিতে পারো

class ApplyPromoCodeSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, data):
        request = self.context.get("request")
        user = request.user
        code = data.get("code")

        # Promo খুঁজে বের করো
        try:
            promo = PromoCode.objects.get(code=code)
        except PromoCode.DoesNotExist:
            raise serializers.ValidationError({"code": "Invalid promo code"})

        # Promo valid কিনা check
        if not promo.is_valid():
            raise serializers.ValidationError({"code": "Promo code expired or inactive"})

        # usage check
        usage, _ = PromoUsage.objects.get_or_create(user=user, promo=promo)
        if usage.used_count >= promo.max_uses_per_user:
            raise serializers.ValidationError({"code": "You have already used this promo code maximum times"})

        # সব ঠিক থাকলে return
        data["promo"] = promo
        data["usage"] = usage
        return data


from .models import ApplyRider,ApplyBuesnessman
# apply as a Bussness and Rider

# Serializer for ApplyRider model
class ApplyRiderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplyRider
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']

# Serializer for ApplyBuesnessman model
class ApplyBuesnessmanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplyBuesnessman
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']
