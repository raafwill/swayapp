from django import forms
from .models import Customer, Seller, Product, Brand, Category, ReceivedItems, Sale, SaleDetail
from django.forms import inlineformset_factory


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'


class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = '__all__'


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['ncm',
                  'brand',
                  'product',
                  'stock_min',
                  'sell_price',
                  'category']


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = '__all__'


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class ReceivedProduct(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product', 'received_by', 'received', 'received_price']


class ReceivedItems(forms.ModelForm):
    class Meta:
        model = ReceivedItems
        exclude = ['product', 'unit_price_payd', 'quantity_received', 'received_by']


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = '__all__'

class SaleDetailForm(forms.ModelForm):
    class Meta:
        model = SaleDetail
        fields = '__all__'
