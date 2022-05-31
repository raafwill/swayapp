from django.contrib import admin
from .models import Customer, Seller, Product, Brand, Category, ReceivedItems, Sale, SaleDetail, ReportedItems

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(ReceivedItems)
admin.site.register(Sale)
admin.site.register(SaleDetail)
admin.site.register(ReportedItems)

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'internal', 'email',
                    'phone', 'created', 'commissioned', 'active')
    date_hierarchy = 'created'
    search_fields = ('firstname', 'lastname')
    list_filter = ('internal', 'commissioned', 'active')
