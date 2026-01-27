from django.contrib import admin
from .models import Product
from django.contrib.auth.admin import UserAdmin


class ProductAdmin(admin.ModelAdmin):
    
    list_display = ('product_name', 'category', 'price', 'stock','is_available')

    prepopulated_fields  = {'slug':('product_name',)}

admin.site.register(Product, ProductAdmin)

# Register your models here.
