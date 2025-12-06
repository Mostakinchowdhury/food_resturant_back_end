from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum,Count,F,Value,FloatField,Case,When,Avg,Window,ExpressionWrapper,Max
from django.db.models.functions import Coalesce
from .serializer import Topcategories,Toppartnersl,Dis_productsserializer
from api.serializers import ApplyRider
from api.models import ApplyRider,Order,ApplyBuesnessman,Product,Category
from rest_framework import status
import math

discount = ExpressionWrapper(
    (F('max_price') - F('price')) / F('max_price') * 100,
    output_field=FloatField()
)

global_info = Product.objects.exclude(max_price__lte=0).aggregate(
    avg_discount=Avg(discount),
    max_discount=Max(discount)
)
offer_product=Product.objects.exclude(max_price__lte=0).annotate(
    discount_percent=discount,
    avr_discount=Value(global_info["avg_discount"], output_field=FloatField())
).filter(discount_percent__gte=F('avr_discount')).order_by('-discount_percent')

# here total count of registered riders's
@api_view()
def myoverview(request):
     total_rider=ApplyRider.objects.all().filter(status="APPROVED").count()
     total_d_orders=Order.objects.all().filter(status="DELIVERED").count()
     total_partner=ApplyBuesnessman.objects.all().filter(status="APPROVED").count()
     total_products=Product.objects.all().count()
     rp={
          "rider_count": total_rider,
          "order_count":total_d_orders,
          "partner_count":total_partner,
          "product_count":total_products
     }
     return Response(rp)

@api_view()
def popular_category(request):
    frq = int(request.query_params.get("count", 6))
    top_categories = Category.objects.annotate(
    total_quantity=Coalesce(Sum('products__orderitem__quantity'),0
    )).order_by('-total_quantity')[:frq]
    result=Topcategories(top_categories,many=True)
    return Response({"top_categories":result.data})

@api_view()
def popularpartner(request):
     frq = int(request.query_params.get("count", 6))
     top_partners = ApplyBuesnessman.objects.annotate(
     total_quantity=Coalesce(Sum('user__products__orderitem__quantity'),0
     ),
     total_products=Coalesce(Count('user__products',distinct=True),0)
     ).order_by('-total_quantity')[:frq]
     result=Toppartnersl(top_partners,many=True)
     return Response({"top_partners":result.data,"length":len(result.data)})

@api_view()
def offercategory(request):
    ctr=set(op.category.name for op in offer_product.order_by("-discount_percent"))
    return Response({
        "categories": ctr,
        "max_discount": math.ceil(global_info["max_discount"]) if global_info["max_discount"] else 0
    })
@api_view()
def Offeruptohalf(request):
     limit=int(request.query_params.get("count", 3))
     category=request.query_params.get("category",None)
     if category is None:
          return Response({"error":"category query param is required"},status=status.HTTP_400_BAD_REQUEST)
     offers=offer_product.all().filter(category__name=category)[:limit] if offer_product.filter(category__name=category).count()>=limit else offer_product.filter(category__name=category)
     result=Dis_productsserializer(offers,many=True,context={'request': request}).data
     return Response({"offers":result,"length":len(result)})


# average product rating
from api.models import ProductRating
@api_view()
def average_Product_Rating(request):
    product_id=request.query_params.get("product_id",None)
    if product_id is None:
        return Response({"error":"product_id query param is required"},status=status.HTTP_400_BAD_REQUEST)
    avr_rating=ProductRating.objects.filter(product__id=product_id).aggregate(avr_rating=Avg('rating'))
    return Response({"average_rating":avr_rating['avr_rating'] if avr_rating['avr_rating'] else 0})


# checking already rated or not
@api_view()
def is_rated_product(request):
    product_id=request.query_params.get("product_id",None)
    user=request.user
    if not user.is_authenticated:
        return Response({"error":"Authentication credentials were not provided."},status=status.HTTP_401_UNAUTHORIZED)
    if product_id is None:
        return Response({"error":"product_id query param is required"},status=status.HTTP_400_BAD_REQUEST)
    prorated=ProductRating.objects.filter(product__id=product_id,user=user)
    is_rated=True if prorated.exists() else False
    rated=prorated.first().rating if is_rated else 0
    return Response({"is_rated":is_rated,"rated":rated})


