from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core import serializers
from django.db.models import ExpressionWrapper, FloatField
from django.db.models.functions import Cast
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, resolve_url
from .models import Customer, Seller, Product, Sale, SaleDetail, ReceivedItems as RC_ITEM, ReportedItems
from .forms import\
    SellerForm, \
    CustomerForm,\
    ReceivedItems,\
    ProductForm,\
    BrandForm,\
    CategoryForm,\
    ReceivedProduct,\
    SaleForm,\
    SaleDetailForm, \
    ReportedItems

from .mixins import CounterMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.db.models import F, Count
from django.forms.models import inlineformset_factory


def index(request, Seller):
    return HttpResponse("teste")


# SEÇÃO VIEWS PARA FORMS DE CADASTROS DE CLIENTES E PRODUTOS
@login_required
def add_seller(request):
    if request.method == 'POST':
        form = SellerForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/swayapp/add_seller/')

    else:
        form = SellerForm()

    return render(request, "sellers.html", {"form": form})

@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/swayapp/add_customer/')

    else:
        form = CustomerForm()

    return render(request, "customers.html", {"form": form})

@login_required
def add_products(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/swayapp/product_list/')
    context = {"form": form,
               "title": "Adicionar Items",
               }
    return render(request, "product_list.html", context)

@login_required
def add_brand(request):
    form = BrandForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/swayapp/add_brand/')
    context = {"form": form,
               "title": "Adicionar Items",
               }
    return render(request, "add_brand.html", context)

@login_required
def add_category(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/swayapp/add_category/')
    context = {"form": form,
               "title": "Adicionar Items",
               }
    return render(request, "add_category.html", context)

@login_required
def receive_product(request, pk):
    queryset = Product.objects.get(id=pk)
    static_price_received = queryset.received_price
    receive_item_form = ReceivedItems(request.POST)
    form = ReceivedProduct(request.POST or None, instance=queryset)

    if form.is_valid() and receive_item_form.is_valid():
        instance = form.save(commit=False)
        receiving = receive_item_form.save(commit=False)
        instance.received_by = request.user #//mudando o model produto received_by para o user que recebeu por ultimo - o que não faz sentido algum
        if receiving.multiplo_check == True:
            instance.stock += instance.received * instance.multiplo
        else:
            instance.stock += instance.received
        receiving.unit_price_payd = instance.received_price
        instance.received_price = instance.received_price + (static_price_received or 0)
        receiving.product = instance.product
        receiving.multiplo = instance.multiplo

        receiving.received_by = instance.received_by
        if receiving.multiplo_check == True:
            receiving.quantity_received = instance.received * instance.multiplo
        else:
            receiving.quantity_received = instance.received

        instance.save()
        receiving.save()

        return redirect('/swayapp/product_list/')

    context = {
        "title": 'Receber ' + str(queryset.product),
        "instance": queryset,
        "receive_item_form": receive_item_form,
        "form": form,
        "username": 'Recebido por'}

    return render(request, "add_products.html", context)


def report_item(request, pk):
    queryset = Product.objects.get(id=pk)
    static_price_received = queryset.received_price
    stock_static = queryset.stock
    custo_medio = static_price_received / stock_static
    reported_item_form = ReportedItems(request.POST)
    form = ReceivedProduct(request.POST or None, instance=queryset)

    if form.is_valid() and reported_item_form.is_valid():
        instance = form.save(commit=False)
        reporting = reported_item_form.save(commit=False)
        instance.stock -= instance.received
        reporting.damage_value = (instance.received * custo_medio)
        instance.received_price = (static_price_received or 0) - (instance.received * custo_medio)
        reporting.product = instance.product

        reporting.reported_by = instance.received_by
        reporting.quantity_lost = instance.received

        instance.save()
        reporting.save()

        return redirect('/swayapp/product_list/')

    context = {
        "title": 'Reportar ' + str(queryset.product),
        "instance": queryset,
        "reported_item_form": reported_item_form,
        "form": form,
        "username": 'recebido por'
    }

    return render(request, "add_products.html", context)



@method_decorator(login_required, name='dispatch')
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

@login_required
def sale_create(request):
    order_forms = Sale()
    item_order_formset = inlineformset_factory(
        Sale,
        SaleDetail,
        form=SaleDetailForm,
        extra=0,
        can_delete=False,
        min_num=1,
        validate_min=True
    )

    if request.method == 'POST':
        forms = SaleForm(request.POST, request.FILES,
                         instance=order_forms, prefix='main')
        formset = item_order_formset(
            request.POST, request.FILES, instance=order_forms, prefix='product')

        if forms.is_valid() and formset.is_valid():
            for form in formset:
                item = form.cleaned_data.get('product')
                qitem = form.cleaned_data.get('quantity')
                Product.objects.filter(product=item).update(received_price=(F('received_price') - (Cast(F('received_price'), output_field=FloatField())/Cast(F('stock'), output_field=FloatField())) * qitem))
                Product.objects.filter(product=item).update(stock=F('stock') - qitem)

            forms = forms.save(commit=False)
            forms.seller = request.user
            forms.save()
            formset.save()



            return HttpResponseRedirect(resolve_url('swayapp:sale_detail', forms.pk))

    else:
        forms = SaleForm(instance=order_forms, prefix='main')
        formset = item_order_formset(instance=order_forms, prefix='product')

        return render(request, 'sale_form.html', {
        'forms': forms,
        'formset': formset})

    context = {
        'forms': forms,
        'formset': formset
    }

    return render(request, 'sale_form.html', context)

@login_required
def autofill(request):
    if 'term' in request.GET:
        qs = Product.objects.filter(Product__icontains=request.GET.get('term'))
        products = list()

        products = [Product.product for product in qs]
        return JsonResponse(products, safe=False)

    return render(request, 'teste.html')

@login_required
def product_price(request):
    products = Product.objects.values('product', 'sell_price')

    data_dict = {}
    for dict in products:
        data_dict[dict['product']] = dict['sell_price']

    return JsonResponse(data_dict)

@method_decorator(login_required, name='dispatch')
class SaleList(CounterMixin, ListView):
    template_name = 'sale_list.html'
    model = Sale
    paginate_by = 60

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


@method_decorator(login_required, name='dispatch')
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


def product_json(request, pk):
    product = Product.objects.filter(pk=pk)
    data = [item.to_dict_json() for item in product]
    return JsonResponse({'data': data})


def product_detail(request, pk):
    queryset = Product.objects.get(id=pk)
    context = {"title": queryset.product,
               "queryset": queryset,}

    return render(request, "product_detail.html", context)


def received_detail(request, pk):
    queryset = RC_ITEM.objects.get(id=pk)
    context = {"title:": "receber " + str(queryset.product),
               "queryset": queryset}

    return render(request, "received_detail.html", context)


def dashboard_with_pivot(request):
    return render(request, 'dashboard_with_pivot.html', {})

def pivot_data(request):
    dataset = SaleDetail.objects.all()
    data = serializers.serialize('json', dataset)
    return JsonResponse(data, safe=False)