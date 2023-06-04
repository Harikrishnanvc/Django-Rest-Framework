from django.contrib import admin
from .models import CustomerAccount, Address, Product, ProductImage, ProductCategory
# Register your models here.
admin.site.register(CustomerAccount)
admin.site.register(Address)
admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(ProductImage)
