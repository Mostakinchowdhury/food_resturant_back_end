
from django.urls import path
from .views import myoverview,popular_category,popularpartner,offercategory,Offeruptohalf,average_Product_Rating,is_rated_product

app_name = 'overview'
urlpatterns = [
   path("ov/",myoverview,name="myoverview"),
   path("tc/",popular_category,name="topcategories"),
   path("tp/",popularpartner,name="toppartners"),
   path("oc/",offercategory,name="offercategory"),
   path("outh/",Offeruptohalf,name="outh"),
   path("apr/",average_Product_Rating,name="apr"),
   path("irp/",is_rated_product,name="irp")
]
