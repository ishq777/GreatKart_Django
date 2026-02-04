from django.contrib import admin
from . models import Payment, Order, OrderProduct


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email','order_total', 'status']
    search_fields = ['phone', 'order_number']
    list_per_page = 15
    
admin.site.register(Payment)

admin.site.register(Order, OrderAdmin)


admin.site.register(OrderProduct)