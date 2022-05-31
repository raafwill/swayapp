from django.urls import path

from . import views

app_name = 'swayapp'

urlpatterns = [
    path('indexteste/', views.index, name='index'),
    path('add_seller/', views.add_seller, name='seller'),
    path('add_customer/', views.add_customer, name='customer'),
    path('add_products/', views.add_products, name='product'),
    path('add_brand/', views.add_brand, name='add_brand'),
    path('add_category/', views.add_category, name='category'),
    path('receive_product/<str:pk>/', views.receive_product, name="receive"),
    path('received_detail/<str:pk>/', views.received_detail, name="received_detail"),
    path('report_item/<str:pk>/', views.report_item, name="report"),
    path('product_list/', views.ProductList.as_view(), name='product_list'),
    path('sale_add/', views.sale_create, name='sale_add'),
    path('<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('sale/', views.SaleList.as_view(), name='sale_list'),
    path('product_price/', views.product_price, name='product_price'),
    path('product_details/<str:pk>/', views.product_detail, name="product_detail"),
    path('sale_add/<int:pk>/json/', views.product_json, name='product_json'),
    path('', views.dashboard_with_pivot, name="dashboard_with_pivot"),
    path('data', views.pivot_data, name='pivot_data'),
]