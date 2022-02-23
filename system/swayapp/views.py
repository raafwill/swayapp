from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, resolve_url
from .models import Customer, Seller, Product, Sale, SaleDetail
from .forms import SellerForm, CustomerForm, ReceivedItems, ProductForm, BrandForm, CategoryForm, ReceivedProduct, \
    SaleForm, SaleDetailForm
from .mixins import CounterMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.db.models import F, Count
from django.forms.models import inlineformset_factory


def index(request, Seller):
    return HttpResponse("teste")


# SEÇÃO VIEWS PARA FORMS DE CADASTROS DE CLIENTES E PRODUTOS
def add_seller(request):
    if request.method == 'POST':
        form = SellerForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/swayapp/add_seller/')

    else:
        form = SellerForm()

    return render(request, "sellers.html", {"form": form})


def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/swayapp/add_customer/')

    else:
        form = CustomerForm()

    return render(request, "customers.html", {"form": form})


def add_products(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/swayapp/add_products/')
    context = {"form": form,
               "title": "Adicionar Items",
               }
    return render(request, "add_products.html", context)


def add_brand(request):
    form = BrandForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/swayapp/add_brand/')
    context = {"form": form,
               "title": "Adicionar Items",
               }
    return render(request, "add_brand.html", context)


def add_category(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/swayapp/add_category/')
    context = {"form": form,
               "title": "Adicionar Items",
               }
    return render(request, "add_category.html", context)


#
# def receive_product(request, pk):
#     queryset = Product.objects.get(id=pk)
#     form = ReceiveProduct(request.POST or None, instance=queryset)
#     if form.is_valid():
#         instance = form.save(commit=False)
#         instance.stock += instance.received
#         instance.save()
#
#         return redirect('/swayapp/product_list/')
#
#     context = {
#         "title": 'Recebido ' + str(queryset.product),
#         "instance": queryset,
#         "form": form,
#         "username": 'Recebido por'}
#     return render(request, "add_products.html", context)


def receive_product(request, pk):
    queryset = Product.objects.get(id=pk)
    static_price_received = queryset.received_price
    receive_item_form = ReceivedItems(request.POST)
    form = ReceivedProduct(request.POST or None, instance=queryset)

    if form.is_valid() and receive_item_form.is_valid():
        instance = form.save(commit=False)
        receiving = receive_item_form.save(commit=False)
        instance.stock += instance.received
        instance.received_price = instance.received_price + static_price_received
        receiving.product = instance.product
        receiving.unit_price_payd = instance.received_price
        receiving.received_by = instance.received_by
        receiving.quantity_received = instance.received

        instance.save()
        receiving.save()

        return redirect('/swayapp/product_list/')

    context = {
        "title": 'Recebido ' + str(queryset.product),
        "instance": queryset,
        "receive_item_form": receive_item_form,
        "form": form,
        "username": 'Recebido por'}

    return render(request, "add_products.html", context)


class ProductList(CounterMixin, ListView):
    template_name = 'product_list.html'
    model = Product
    paginate_by = 15
    form_class = ProductForm

    def get_context_data(self):
        context = super(ProductList, self).get_context_data()
        context['form'] = ProductForm
        return context

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/swayapp/add_products/')
        else:
            messages.error(request, "Error")

        return render(request, self.template_name, {"form": form})

    def get_queryset(self):
        p = Product.objects.all()
        q = self.request.GET.get('search_box')
        # buscar por produto
        if q is not None:
            p = p.filter(product__icontains=q)
        # filtra produtos em baixo estoque
        if self.request.GET.get('filter_link', False):
            p = p.filter(stock__lt=F('stock_min'))
        # filtra produtos fora de linha
        if self.request.GET.get('outofline', False):
            p = p.filter(outofline=1)
        return p


def sale_create(request):
    order_forms = Sale()
    item_order_formset = inlineformset_factory(
        Sale, SaleDetail, form=SaleDetailForm, extra=0, can_delete=False,
        min_num=1, validate_min=True
    )

    if request.method == 'POST':
        forms = SaleForm(request.POST, request.FILES,
                         instance=order_forms, prefix='main')
        formset = item_order_formset(
            request.POST, request.FILES, instance=order_forms, prefix='product')

        if forms.is_valid() and formset.is_valid():
            forms = forms.save()
            formset.save()
            return HttpResponseRedirect(resolve_url('swayapp:sale_detail', forms.pk))

    else:
        forms = SaleForm(instance=order_forms, prefix='main')
        formset = item_order_formset(instance=order_forms, prefix='product')

    context = {
        'forms': forms,
        'formset': formset
    }

    return render(request, 'sale_form.html', context)


class SaleList(CounterMixin, ListView):
    template_name = 'sale_list.html'
    model = Sale
    paginate_by = 20

    def get_queryset(self):

        if 'filter_sale_one' in self.request.GET:
            return Sale.objects.annotate(
                itens=Count('sales_det')).filter(itens=1)

        if 'filter_sale_zero' in self.request.GET:
            return Sale.objects.annotate(
                itens=Count('sales_det')).filter(itens=0)

        qs = super(SaleList, self).get_queryset()

        if 'customer' in self.request.GET:
            qs = qs.filter(customer=self.request.GET['customer'])
        if 'seller' in self.request.GET:
            qs = qs.filter(seller=self.request.GET['seller'])

        return qs


class SaleDetailView(DetailView):
    template_name = 'sale_detail.html'
    model = Sale
    context_object_name = 'Sale'

    def get_context_data(self, **kwargs):
        sd = SaleDetail.objects.filter(sale=self.object)
        context = super(SaleDetailView, self).get_context_data(**kwargs)
        context['count'] = sd.count()
        context['Itens'] = sd
        return context
