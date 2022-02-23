from django.db import models
from django.utils.formats import number_format
from django.urls import reverse_lazy

gender_list = [('M', 'masculino'), ('F', 'feminino')]


# creating a class time stamp
class TimeStampedModel(models.Model):
    created = models.DateTimeField(
        'criado em', auto_now_add=True, auto_now=False)
    modified = models.DateTimeField(
        'modificado em', auto_now_add=False, auto_now=True)

    class Meta:
        abstract = True


# seção de model para criação de personas
class Person(TimeStampedModel):
    """ Person is abstract model"""
    gender = models.CharField('gênero', max_length=1, choices=gender_list)
    cpf = models.CharField('CPF', max_length=11)
    firstname = models.CharField('Nome', max_length=20)
    lastname = models.CharField('Sobrenome', max_length=20)
    email = models.EmailField('e-mail', unique=True, blank=True)
    phone = models.CharField('Fone', max_length=18, blank=True)
    birthday = models.DateTimeField('Nascimento', blank=True)

    class Meta:
        abstract = True
        ordering = ['firstname']

    def __str__(self):
        return self.firstname + " " + self.lastname

    full_name = property(__str__)


class Customer(Person):
    pass

    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'

    # click on the customer and get it details
    def get_customer_url(self):
        return "/customer/%i" % self.id

    def get_sale_customer_url(self):
        return "/sale/?customer=%i" % self.id

    def get_sales_count(self):
        return self.customer_sale.count()


class Seller(Person):
    active = models.BooleanField('ativo', default=True)
    internal = models.BooleanField('interno', default=True)
    commissioned = models.BooleanField('comissionado', default=True)
    commission = models.DecimalField('comissão', max_digits=6, decimal_places=2, default=0.01, blank=True)

    class Meta:
        verbose_name = 'vendedor'
        verbose_name_plural = 'vendedores'

    # click on the customer and get it details
    def get_seller_url(self):
        return "/seller/%i" % self.id

    # click on the sales and get it details
    def get_sale_seller_url(self):
        return "/sale/?seller=%i" % self.id

    # sales per person
    def get_sales_count(self):
        return self.seller_sale.count()

    def get_commission(self):
        return "%s" % number_format(self.commission * 100, 0)


# models para criação de produtos
class Brand(models.Model):
    brand = models.CharField('Marca', max_length=50, unique=True)

    class Meta:
        ordering = ['brand']
        verbose_name = 'Marca'
        verbose_name_plural = 'marcas'

    def __str__(self):
        return self.brand


class Category(models.Model):
    id = models.CharField('Id', max_length=7, primary_key=True)
    category = models.CharField('Categoria', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.category


class Product(models.Model):
    imported = models.BooleanField('Importado', default=False)
    outofline = models.BooleanField('Fora de Linha', default=False)
    ncm = models.CharField('NCM', max_length=8)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        verbose_name='marca'
    )
    product = models.CharField('Produto', max_length=100, unique=True)
    sell_price = models.DecimalField('Preço venda', max_digits=7, decimal_places=2, default=0)
    received_by = models.CharField(max_length=50, blank=True, null=True)
    received = models.IntegerField(default='0', blank=False, null=True)
    received_price = models.DecimalField('Preço Recebimento', max_digits=20, decimal_places=2, null=True)
    ipi = models.DecimalField('IPI', max_digits=3, decimal_places=2, blank=True, default=0)
    stock = models.IntegerField('Estoque atual', default='0', blank=False, null=True)
    stock_min = models.PositiveIntegerField('Estoque Minimo', default=0)
    category = models.ForeignKey(Category, verbose_name='Categoria', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['product']
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return self.product

    def get_price(self):
        return "R$ %s" % number_format(self.sell_price, 2)

    def get_ipi(self):
        return "%s" % number_format(self.ipi * 100, 0)

    def get_custo_medio(self):
        if self.stock != 0 and self.received_price != 0:
            return "R$ %s" % number_format(self.received_price / self.stock, 2)
        else:
            return "R$ %s" % number_format(0, 2)


# seção de criação de modelos de vendas
class Sale(TimeStampedModel):
    customer = models.ForeignKey('Customer', related_name='customer_sale', verbose_name='cliente',
                                 on_delete=models.CASCADE)
    seller = models.ForeignKey('Seller', related_name='seller_sale', verbose_name='vendedor', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'venda'
        verbose_name_plural = 'vendas'

    def __str__(self):
        return "%03d" % self.id + "/%s" % self.created.strftime('%y')

    codigo = property(__str__)

    def get_absolute_url(self):
        return reverse_lazy('swayapp:sale_detail', pk=self.pk)

    def get_detail(self):
        return "/swayapp/%i" % self.id

    def get_items(self):
        return self.sales_det.count()

    def get_total(self):
        qs = self.sales_det.filter(sale=self.pk).values_list('price_sale', 'quantity') or 0
        t = 0 if isinstance(qs, int) else sum(map(lambda q: q[0] * q[1], qs))
        return "R$ %s" % number_format(t, 2)


class SaleDetail(models.Model):
    sale = models.ForeignKey(
        Sale,
        related_name="sales_det",
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        related_name='product_det',
        verbose_name='produto',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveSmallIntegerField('quantidade')
    price_sale = models.DecimalField(
        'Preço de venda',
        max_digits=20,
        decimal_places=2,
        default=0
    )

    ipi_sale = models.DecimalField(
        'IPI', max_digits=3, decimal_places=2, default=0.1
    )

    def __str__(self):
        return str(self.sale)

    def get_subtotal(self):
        return self.price_sale * (self.quantity or 0)

    subtotal = property(get_subtotal)

    def getID(self):
        return "%04d" % self.id

    def price_sale_formated(self):
        return "R$ %s" % number_format(self.price_sale, 2)

    def get_ipi(self):
        return "%s" % number_format(self.ipi_sale * 100, 0)

    def get_subtotal_formated(self):
        return "R$ %s" % number_format(self.subtotal, 2)


class ReceivedItems(models.Model):
    product = models.CharField(max_length=50, blank=True, null=True)
    unit_price_payd = models.DecimalField('Custo', max_digits=20, decimal_places=2, default=0)
    quantity_received = models.IntegerField('Quantidade', default='0', blank=False, null=True)
    received_by = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['product']
        verbose_name = 'Received'
        verbose_name_plural = 'Receiveds'

    def __str__(self):
        return self.product

    def get_total_payd(self):
        return self.unit_price_payd * (self.quantity_received or 0)

    total = property(get_total_payd)
