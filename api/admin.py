from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Setting, Order, Tag, Profile, Category, Product, ProductReview, Cart, CartItem, subscribers, Address,PromoCode,OrderItem,PromoUsage,Product_images,Supercategory,ApplyRider,ApplyBuesnessman,OrderProvedByRider

# Register your models here.
User=get_user_model()
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
# deafalt register all model except user model
admin.site.register(Profile)
admin.site.register(Tag)
admin.site.register(Setting)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductReview)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(subscribers)
admin.site.register(Address)
admin.site.register(PromoCode)
admin.site.register(PromoUsage)
admin.site.register(Product_images)
admin.site.register(Supercategory)
admin.site.register(ApplyRider)
admin.site.register(ApplyBuesnessman)
admin.site.register(OrderItem)
admin.site.register(OrderProvedByRider)
@admin.register(Order)
class CustomOrderAdmin(admin.ModelAdmin):
    list_display = (
        'user',
       'cart',
    'status',
    'address',
   'phone',
    'is_cashon',
    'ordered_at',
    'amount',
    'orderitems_string'
    )
    search_fields = ['id']
    list_filter = ('status',)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "fullname",
        "is_verified",
        "get_language",
        "order_count",
        "get_tags",
    )
    ordering=("email",)
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("created_at","updated_at","otp_code","otp_expiry")
    list_filter = ("is_staff", "is_active", "is_superuser", "groups")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name","is_verified",)}),
        ("Extra Info", {"fields": ("created_at","updated_at","otp_code","otp_expiry")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2", "is_staff", "is_active", "is_superuser")}
        ),
    )

    def fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    fullname.short_description = "Full Name"

    def get_language(self, obj):
        setting = Setting.objects.filter(user=obj).first()
        return setting.language if setting else "N/A"
    get_language.short_description = "Language"

    def order_count(self, obj):
        return Order.objects.filter(user=obj).count()
    order_count.short_description = "Total Orders"

    def get_tags(self, obj):
        tags = Tag.objects.filter(tag_author=obj)
        return ", ".join(tag.name for tag in tags)
    get_tags.short_description = "Tags"



# register profile,tag,setting model in admin panel



