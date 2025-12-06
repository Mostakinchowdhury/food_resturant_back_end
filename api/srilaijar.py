from rest_framework import serializers
from .models import ProductRating

# Product review serializer
class ProductretingSerializer(serializers.ModelSerializer):
    userName = serializers.SlugRelatedField(slug_field="email", read_only=True,source="user")
    productName = serializers.SlugRelatedField(slug_field="name", read_only=True,source="product")
    class Meta:
        model = ProductRating
        fields = ['id', 'product', 'user','productName','userName', 'rating', 'created_at','updated_at']
        read_only_fields = ['id', 'productName',"user",'userName', 'created_at','updated_at']

