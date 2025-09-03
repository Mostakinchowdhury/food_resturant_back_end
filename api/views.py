# api/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly,IsOwner
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import (
    Profile, Setting, Tag, Order, Product,
    Category, Cart, CartItem, ProductReview
)
from .serializers import (
    ProfileSerializer, SettingSerializer, TagSerializer,
    OrderSerializer, ProductSerializer, CategorySerializer,
    CartSerializer, CartItemSerializer, UserRegistrationSerializer,
    loginserializer, ChangePasswordSerializer,
    ResetPasswordgenaretSerializer, setResetPasswordSerializer,ProductReviewSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
User = get_user_model()

# function to get tokens for user
def get_tokens_for_user(user):
    if not user.is_active:
      raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# 🔹 Profile ViewSet
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes=[MultiPartParser, FormParser, JSONParser]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    get_queryset = lambda self: self.queryset.filter(user=self.request.user)

# 🔹 Setting ViewSet
class SettingViewSet(viewsets.ModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    get_queryset = lambda self: self.queryset.filter(user=self.request.user)


# 🔹 Tag ViewSet
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]
    def perform_create(self, serializer):
        serializer.save(tag_author=self.request.user)
    def perform_update(self, serializer):
        serializer.save(tag_author=self.request.user)

# 🔹 Category ViewSet
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes=[MultiPartParser, FormParser, JSONParser]

from .pagination import CustomPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
# 🔹 Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes=[MultiPartParser, FormParser, JSONParser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['price', 'created_at']
    search_fields = ['name', 'description', 'category__name', 'tags__tag_name']
    filterset_fields = ['category__name', 'tags__tag_name']
    ordering=['-created_at']
# 🔹 Cart ViewSet
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated,IsOwner]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    get_queryset = lambda self: self.queryset.filter(user=self.request.user)

# 🔹 CartItem ViewSet
class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(cart=self.request.user.cart)
    def perform_update(self, serializer):
        serializer.save(cart=self.request.user.cart)
    get_queryset = lambda self: self.queryset.filter(cart__user=self.request.user)
    @action(detail=False, methods=["post"], url_path="add-to-cart")
    def add_to_cart(self, request):
        product_id = request.data.get("product_id")
        cartitems, created = CartItem.objects.get_or_create(
            cart=request.user.cart,
            product_id=product_id,
        )
        if not created:
            cartitems.quantity += 1
            cartitems.save()
        serializer = self.get_serializer(cartitems)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 🔹 Order ViewSet
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 🔹 ProductReview ViewSet
class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

# 🔹 Registration
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            res=serializer.save()
            return Response(res,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # login users serialize data
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserRegistrationSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 🔹 Login
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = loginserializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message":"Congratulation you are succesfully loged in",**serializer.validated_data['token']}, status=status.HTTP_200_OK)

# 🔹 Change Password
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully",'user':serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔹 Password Reset (Send Email)
class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = ResetPasswordgenaretSerializer(data=request.data)
        if serializer.is_valid():
            msg = serializer.save()
            return Response({"message": msg}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔹 Password Reset (Set New Password)
class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = setResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"success": "Password reset successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.utils import timezone
from .utils import send_otp_via_email
# verify email with otp when user register

class verify_register_otp(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        otp = request.data.get("otp")
        email = request.POST.get("email")
        if not otp:
            return Response({"error": "OTP is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
         user = User.objects.get(email=email)
        except User.DoesNotExist:
           return Response({"error": "User not found try again"}, status=status.HTTP_404_NOT_FOUND)

        if user.otp_code == otp and user.otp_expiry > timezone.now():
           user.is_verified = True
           user.otp_code = None
           user.save()
           token=get_tokens_for_user(user)
           return Response({"message": "Email verified successfully",'tokens':token}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or expired OTP. Click the Resend OTP button to try again."}, status=status.HTTP_400_BAD_REQUEST)

    # resend otp if user click the resend otp button by get method
    def get(self, request):
        email = request.GET.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
         user = User.objects.get(email=email)
        except User.DoesNotExist:
           return Response({"error": "User not found try again"}, status=status.HTTP_404_NOT_FOUND)
        if user.is_verified:
            return Response({"message": "Your email is already verified, please log in."}, status=status.HTTP_200_OK)
        send_otp_via_email(user)
        return Response({"message": "A new OTP has been sent to your email. Check it and fill in the OTP input."}, status=status.HTTP_200_OK)
