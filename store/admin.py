from django.contrib import admin
from .models import Product, Variation
from django.contrib.auth.admin import UserAdmin


class ProductAdmin(admin.ModelAdmin):
    
    list_display = ('product_name', 'category', 'price', 'stock','is_available')

    prepopulated_fields  = {'slug':('product_name',)}

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category','variation_value', 'created_date', 'is_active')
    list_editable = ['is_active']


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)

# Register your models here.
