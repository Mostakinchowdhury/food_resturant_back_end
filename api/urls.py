
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet, SettingViewSet, TagViewSet,OrderItemViewSet,
    CategoryViewSet, ProductViewSet, CartViewSet,
    CartItemViewSet, OrderViewSet, ProductReviewViewSet,
    RegisterView, LoginView, ChangePasswordView,
    PasswordResetRequestView, PasswordResetConfirmView, verify_register_otp, Adressviewset, Subscribersviewset,
    PromoCodeListCreateView, ApplyPromoCodeView,SupercategoryViewSet,SSLCommerzCheckoutView,Product_imagesViewSet, payment_success,
    payment_fail, payment_cancel, stripe_webhook, wellcome,delete_unverified_users
)
from rest_framework_simplejwt.views import (
     TokenRefreshView,TokenBlacklistView,TokenVerifyView
)
app_name = 'api'
router = DefaultRouter()
router.register("profiles", ProfileViewSet, basename="profiles")
router.register("settings", SettingViewSet, basename="settings")
router.register("tags", TagViewSet, basename="tags")
router.register("categories", CategoryViewSet, basename="categories")
router.register("products", ProductViewSet, basename="products")
router.register("carts", CartViewSet, basename="carts")
router.register("cart-items", CartItemViewSet, basename="cart-items")
router.register("orders", OrderViewSet, basename="orders")
router.register("reviews", ProductReviewViewSet, basename="reviews")
router.register("adress", Adressviewset, basename="adress")
router.register("subscribers", Subscribersviewset, basename="subscribers")
router.register("product_images", Product_imagesViewSet, basename="product_images")
router.register("supercategory", SupercategoryViewSet, basename="supercategory")
router.register("supercategories", SupercategoryViewSet, basename="supercategories")
router.register("product-images", Product_imagesViewSet, basename="product-images")
router.register("orderItems", OrderItemViewSet, basename="OrderItemViewSet")

urlpatterns = [
    path("", include(router.urls)),
    # User auth
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),

    # Password reset
    path("auth/request-reset-password/", PasswordResetRequestView.as_view(), name="request-reset-password"),
    path("auth/reset-password-confirm/", PasswordResetConfirmView.as_view(), name="reset-password-confirm"),
    path('auth/verify_user_otp/',verify_register_otp.as_view(),name="verify_user_otp"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('auth/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('promocodes/', PromoCodeListCreateView.as_view(), name='promo-list-create'),
    path('promocodes/apply/', ApplyPromoCodeView.as_view(), name='promo-apply'),
    path("sslcommerz-checkout/<int:pk>/", SSLCommerzCheckoutView.as_view()),
    path('payment/success/',payment_success),
    path('payment/cancel/',payment_cancel),
    path('payment/fail/',payment_fail),
    path('stripe_webhook/',stripe_webhook),
    path('wellcome/',wellcome),
    # crone job
    path("cronejob/delete_unverified_users/",delete_unverified_users)
]

