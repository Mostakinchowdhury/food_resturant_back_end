from api.models import Category,ApplyBuesnessman
from rest_framework import serializers
from api.models import Product
from api.serializers import ProductSerializer
class Topcategories(serializers.ModelSerializer):
    total_quantity = serializers.IntegerField()
    class Meta:
        model = Category
        fields = ["id", "name", "description","image","total_quantity"]
        read_only_fields = ['id',]

class Toppartnersl(serializers.ModelSerializer):
    total_quantity = serializers.IntegerField()
    total_products = serializers.IntegerField()
    class Meta:
        model = ApplyBuesnessman
        fields = [
            'id',
            'name',
            'email',
            'phone_num',
            'business_name',
            'business_address',
            'business_type',
            'website',
            'description',
            'buesness_logo',
            'owner_photo',
            'status',
            'created_at',
            'updated_at',
            'total_quantity',
            'total_products'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class Dis_productsserializer(serializers.ModelSerializer):
     category=serializers.SlugRelatedField(slug_field="name",read_only=True)
     productimgs=serializers.SerializerMethodField()
     added_to_cart_count = serializers.IntegerField(read_only=True)
     discount_percent=serializers.FloatField(read_only=True)
     avr_discount=serializers.FloatField(read_only=True)
     class Meta:
        model = Product
        fields = ["id",'category',"productimgs",'name',"discount_percent","avr_discount","added_to_cart_count"]
        read_only_fields = ['id','category','create_at','update_at','tags','reviews','average_rating','review_count','addedtocard','added_to_cart_count']
     def get_productimgs(self, obj):
        request = self.context.get('request',None)
        if request is None:
            return None
        img = obj.productimgs.all().first()
        return request.build_absolute_uri(img.file.url) if img else None
