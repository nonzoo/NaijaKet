from django.urls import path

from . import views

urlpatterns = [
    path('search/', views.search, name='search'),
    path('search/suggestions/', views.search, name='search-suggestions'),
    path('<slug:slug>/', views.category_detail, name='category_detail'),
    path('<slug:category_slug>/<slug:subcategory_slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('<str:category_slug>/<str:subcategory_slug>/<str:slug>/', views.product_detail, name='product_detail'),

]
#path('cart/success/', views.success, name='success'),
'''path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('change-quantity/<str:product_id>/', views.change_quantity, name='change_quantity'),
    path('remove-from-cart/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/checkout/', views.checkout, name='checkout'),'''
#path('category/<str:category_slug>/<str:slug>/', views.product_detail, name='product_detail_no_subcategory'),