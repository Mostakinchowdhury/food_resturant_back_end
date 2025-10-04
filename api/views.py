# api/views.py
from pyexpat.errors import messages
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly, IsOwner, onlygetandcreate, IsadressOwner
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import (
    Profile, Setting, Tag, Order, Product,
    Category, Cart, CartItem, ProductReview, Address,OrderItem
)
from .serializers import (
    ProfileSerializer, SettingSerializer, TagSerializer,
    OrderSerializer, ProductSerializer, CategorySerializer,
    CartSerializer, CartItemSerializer, UserRegistrationSerializer,
    loginserializer, ChangePasswordSerializer,
    ResetPasswordgenaretSerializer,OrderItemSerializer, setResetPasswordSerializer, ProductReviewSerializer, adressserializer
)
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY
from threading import Thread
from .utils import  send_welcome_email
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
User = get_user_model()
from django.db.models.functions import Coalesce
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
from django.db.models import Sum,Value
from django.db.models import F, ExpressionWrapper, FloatField


# 🔹 Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.annotate(
        added_to_cart_count=Coalesce(Sum('cartitem__quantity'), 0)
    )
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes=[MultiPartParser, FormParser, JSONParser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['price', 'created_at','added_to_cart_count']
    search_fields = ['name', 'description', 'category__name', 'tags__name']
    ordering=['-created_at']


    @action(detail=False, methods=["GET"])
    def discount_items(self, request):
        # discount শতাংশ হিসাব
        discount_expr = ExpressionWrapper(
            (F('max_price') - F('price')) * 100.0 / F('max_price'),
            output_field=FloatField()
        )

        # annotate + filter + order_by
        qs = Product.objects.annotate(discount_percent=discount_expr).filter(
            max_price__isnull=False,
            max_price__gt=0,
            price__lt=F('max_price')   # শুধুমাত্র discount আছে এমন product
        ).order_by('-discount_percent')

        # pagination apply
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
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
    @action(detail=False, methods=["post"])
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
    filter_backends = [OrderingFilter]
    ordering = ['-ordered_at']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,orderitems_string=",".join(f"{item.product.id}:{item.product.name} x {item.quantity}" for item in
                                       self.request.user.cart.items.checked_items()))

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    # payment section
    @action(detail=False, methods=["post"])
    def online_payment(self, request):
        cash_order = Order.objects.create(
            user=request.user,
            cart=request.user.cart,
            address=f"{request.data.get('city')},{request.data.get('street')},{request.data.get('country')}",
            phone=f"{request.data.get('phone')}",
            amount=request.data.get('amount'),
            orderitems_string=",".join(f"{item.product.id}:{item.product.name} x {item.quantity}" for item in
                                       request.user.cart.items.checked_items()),

        )
        order = get_object_or_404(Order, pk=cash_order.pk)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": order.currency,
                    "product_data": {"name": item.product.name},
                    "unit_amount": int(item.product.price * 100),  # cents
                },
                "quantity": item.quantity,
            } for item in order.cart.items.checked_items()],
            mode="payment",
            success_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/cancel",
            metadata={"order_id": str(order.id)},
        )
        cheakeditems=CartItem.objects.checked_items()
        for item in cheakeditems:
            OrderItem.objects.create(
                order=cash_order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price)
            item.delete()
        return Response({"url": checkout_session.url,"messages":"Order is ready for payment"})
    # cash_on_delivery action
    @action(detail=False, methods=["post"])
    def cash_on_delivery(self, request):
        cash_order=Order.objects.create(
            user=request.user,
            cart=request.user.cart,
            status='CASHANDPROCESSING',
            address=f"{request.data.get('city')},{request.data.get('street')},{request.data.get('country')}",
            phone=f"{request.data.get('phone')}",
            is_cashon=True,
            amount=request.data.get('amount'),
            orderitems_string=",".join(f"{item.product.id}:{item.product.name} x {item.quantity}" for item in
                                       request.user.cart.items.checked_items()),
        )

        cheakeditems = CartItem.objects.checked_items()
        # cartitem to orderitem convert and cartitem delete
        for item in cheakeditems:
            OrderItem.objects.create(
                order=cash_order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price)
            item.delete()
        serializer = self.get_serializer(cash_order)
        return Response({'messages':"Order succesfully placed",'result':serializer.data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def Ispercheased(self, request):
         product_id = request.GET.get("product_id")
         if not product_id:
             return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
         has_purchased = Order.objects.filter(
             user=request.user,
             orderitems__product_id=product_id,
             status__in=['PAIDANDPROCESSING', 'DELIVERED', 'CASHANDPROCESSING']
         ).exists()
         return Response({"has_purchased": has_purchased}, status=status.HTTP_200_OK)
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
        email = request.data.get("email")
        if not otp:
            return Response({"error": "OTP is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
         user = User.objects.get(email=email)
         if user.is_verified:
             return Response({"error": "Email is already verified"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
           return Response({"error": "User not found try again"}, status=status.HTTP_404_NOT_FOUND)

        if user.otp_code == otp and user.otp_expiry > timezone.now():
           user.is_verified = True
           user.otp_code = None
           user.save()
           Thread(target=send_welcome_email, args=[user]).start()
           token=get_tokens_for_user(user)
           Profile.objects.create(user=user)
           Setting.objects.create(user=user)
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



# subscriber view
from .permissions import onlygetandcreate
from .models import subscribers,Address
from .serializers import subscribersserializer,adressserializer

class Subscribersviewset(viewsets.ModelViewSet):
    queryset = subscribers.objects.all()
    serializer_class = subscribersserializer
    permission_classes = [onlygetandcreate]

class Adressviewset(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = adressserializer
    permission_classes = [permissions.IsAuthenticated,IsadressOwner]


# coupe on code view

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import PromoCode
from .serializers import PromoCodeSerializer, ApplyPromoCodeSerializer

# Promo code create & list view
class PromoCodeListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer


# Promo Code Apply View
class ApplyPromoCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        serializer = ApplyPromoCodeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        promo = PromoCode.objects.get(code=code)
        usage = serializer.validated_data["usage"]

        # use count +1
        promo.used_count += 1
        promo.save()
        usage.used_count += 1
        usage.save()

        return Response({
            "message": f"Promo Code {promo.code} applied successfully!",
            "success": True,
            "code": promo.code,
            "discount_percent": promo.discount_percent,
            "remaining_uses": promo.max_uses_per_user - usage.used_count
        }, status=status.HTTP_200_OK)




# stripe webhook
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    endpoint_secret=settings.STRIPE_WEBHOOK_SECRET
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('Error parsing payload: {}'.format(str(e)))
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('Error verifying webhook signature: {}'.format(str(e)))
        return HttpResponse(status=400)
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session["metadata"]["order_id"]
        order = Order.objects.get(id=order_id)
        order.status = "PAIDANDPROCESSING"
        order.save()

    return HttpResponse(status=200)


# sslcommers set up for python django

from sslcommerz_lib import SSLCOMMERZ
from django.conf import settings

class SSLCommerzCheckoutView(APIView):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        settings_dict = {
            'store_id': settings.SSLCOMMERZ_STORE_ID,
            'store_pass': settings.SSLCOMMERZ_STORE_PASS,
            'issandbox': True
        }
        sslcz = SSLCOMMERZ(settings_dict)

        post_body = {
            'total_amount': str(order.amount),
            'currency': order.currency,
            'tran_id': str(order.id),
            'success_url': "http://127.0.0.1:8000/api/payment/success/",
            'fail_url': "http://127.0.0.1:8000/api/payment/fail/",
            'cancel_url': "http://127.0.0.1:8000/api/payment/cancel/",
            'cus_name': "Test User",
            'cus_email': "test@test.com",
            'cus_phone': "01700000000",
            'cus_add1': "Dhaka",
            'cus_country': "Bangladesh",
            'product_name': "demo",
            'cus_city':"dhaka",
            'product_category': "General",
            'product_profile': "general",
            'shipping_method':'NO'
        }

        response = sslcz.createSession(post_body)
        return Response({"url": response["GatewayPageURL"],**response})


# sucess page
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def payment_success(request):
    tran_id = request.POST.get("tran_id") or request.GET.get("tran_id")
    if not tran_id:
        return HttpResponseBadRequest("Transaction ID missing")

    try:
        order = Order.objects.get(id=tran_id)
    except Order.DoesNotExist:
        return HttpResponseBadRequest("Order does not exist")

    order.status = "PAIDANDPROCESSING"
    order.save()
    return HttpResponse("Payment Success")

# cancel page
@csrf_exempt
def payment_cancel(request):
    tran_id = request.POST.get("tran_id") or request.GET.get("tran_id")
    if not tran_id:
        return HttpResponseBadRequest("Transaction ID missing")

    try:
     order = Order.objects.get(id=tran_id)
    except Order.DoesNotExist:
        return HttpResponseBadRequest("Order does not exist")
    order.status = "CANCELLED"
    order.save()
    return HttpResponse("Payment Cancelled")
@csrf_exempt
def payment_fail(request):
    tran_id = request.POST.get("tran_id") or request.GET.get("tran_id")
    order = Order.objects.get(id=tran_id)
    if not tran_id:
        return HttpResponseBadRequest("Transaction ID missing")

    try:
     order = Order.objects.get(id=tran_id)
    except Order.DoesNotExist:
        return HttpResponseBadRequest("Order does not exist")
    order.status = "CANCELLED"
    order.save()
    return HttpResponse("Payment Failed")


from django.http import HttpResponse
from .models import Supercategory,Product_images
from .serializers import SupercategorySerializer,ProductimgsSerializer
from .permissions import IsAdminOrReadOnly
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import ApplyRider, ApplyBuesnessman
from .serializers import ApplyRiderSerializer, ApplyBuesnessmanSerializer


# Supercategory view
class SupercategoryViewSet(viewsets.ModelViewSet):
    queryset = Supercategory.objects.all()
    serializer_class = SupercategorySerializer
    permission_classes = [IsAdminOrReadOnly]

#Product_images view

class Product_imagesViewSet(viewsets.ModelViewSet):
    queryset = Product_images.objects.all()
    serializer_class = ProductimgsSerializer
    permission_classes = [IsAdminOrReadOnly]




# apply rider and buesness viewset

# ApplyRider ViewSet
class ApplyRiderViewSet(viewsets.ModelViewSet):
    queryset = ApplyRider.objects.all()
    serializer_class = ApplyRiderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# ApplyBuesnessman ViewSet
class ApplyBuesnessmanViewSet(viewsets.ModelViewSet):
    queryset = ApplyBuesnessman.objects.all()
    serializer_class = ApplyBuesnessmanSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# wellcome view

def wellcome(request):
    return HttpResponse("welcome i am alive...")

# cron job for is_verified fail user delete thats hit by uptimerobot
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse,HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
User = get_user_model()
@csrf_exempt
def delete_unverified_users(request):
    if not request.method in permissions.SAFE_METHODS:
        return HttpResponseForbidden("Only SAFE METHODS is allowed.")

    # ১ ঘন্টার বেশি পুরানো এবং is_verified=False এমন user গুলো খুঁজে বের করা
    cutoff = timezone.now() - timedelta(minutes=5)
    unverified_users = User.objects.filter(is_verified=False, updated_at__lt=cutoff).exclude(is_staff=True).exclude(is_superuser=True)
    # apply rider and buesnessman application গুলো ডিলিট করা
    canceled_rideds=ApplyRider.objects.filter(status="CANCELLED",updated_at__lt=cutoff)
    canceled_buesnessman=ApplyBuesnessman.objects.filter(status="CANCELLED",updated_at__lt=cutoff)
    # user গুলো delete করা
    count = unverified_users.count()
    if count > 0:
      unverified_users.delete()

    if canceled_rideds.count()>0:
     canceled_rideds.delete()
    if canceled_buesnessman.count()>0:
      canceled_buesnessman.delete()
    return HttpResponse(f"Deleted {count} unverified users. Deleted {canceled_rideds.count()} canceled rider record. Deleted {canceled_buesnessman.count()} canceled business record.")



# orderitems viewset
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated,IsOwner]
    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)
