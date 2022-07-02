from django import forms
from .models import Customer, Seller, Product, Brand, Category, ReceivedItems, Sale, SaleDetail, ReportedItems
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
                  'multiplo',
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
        fields = ['received', 'received_price']


class ReceivedItems(forms.ModelForm):
    class Meta:
        model = ReceivedItems
        exclude = ['product', 'unit_price_payd', 'quantity_received', 'received_by', 'multiplo']

class ReportedItems(forms.ModelForm):
    class Meta:
        model = ReportedItems
        exclude = ['product', 'damage_value', 'quantity_lost', 'reported_by', 'received_price']


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer']

class SaleDetailForm(forms.ModelForm):
    class Meta:
        model = SaleDetail
        fields = ['sale', 'product',  'quantity', 'price_sale']
