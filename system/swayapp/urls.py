from django.urls import path

from . import views

app_name = 'swayapp'

urlpatterns = [
    path('indexteste/', views.index, name='index'),
    path('add_seller/', views.add_seller, name='seller'),
    path('add_customer/', views.add_customer, name='customer'),
    path('add_products/', views.add_products, name='product'),
    path('add_brand/', views.add_brand, name='brand'),
    path('add_category/', views.add_category, name='category'),
    path('receive_product/<str:pk>/', views.receive_product, name="receive"),
    path('product_list/', views.ProductList.as_view(), name='product_list'),
    path('sale_add/', views.sale_create, name='sale_add'),
    path('<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('sale/', views.SaleList.as_view(), name='sale_list')
]