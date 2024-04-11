from django.contrib import admin

from .models import Category, Product,Subcategory

admin.site.register(Category)


@admin.register(Subcategory)
class Subcategory(admin.ModelAdmin):
    search_fields = ['title']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','user','price', 'category','condition','created_at']
    search_fields = ['user__username', 'title', 'condition']
    list_per_page = 50 
    list_filter = ['status']







#admin.site.register(OrderItem)
#admin.site.register(Order)