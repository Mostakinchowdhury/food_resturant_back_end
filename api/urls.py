from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet, SettingViewSet, TagViewSet,
    CategoryViewSet, ProductViewSet, CartViewSet,
    CartItemViewSet, OrderViewSet, ProductReviewViewSet,
    RegisterView, LoginView, ChangePasswordView,
    PasswordResetRequestView, PasswordResetConfirmView,verify_register_otp
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

urlpatterns = [
    path("", include(router.urls)),

    # User auth
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),

    # Password reset
    path("auth/request-reset-password/", PasswordResetRequestView.as_view(), name="request-reset-password"),
    path("auth/reset-password-confirm/", PasswordResetConfirmView.as_view(), name="reset-password-confirm"),
    path('verify_user_otp/',verify_register_otp.as_view(),name="verify_user_otp"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
