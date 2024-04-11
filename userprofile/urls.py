from django.urls import path
from django.contrib.auth import views as auth_views
from . import views



urlpatterns = [
    path('privacy/', views.privacy, name='privacy'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.loginView ,name='login'),
    path('logout/', views.logoutUser, name='logout'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='userprofile/password_change_form.html'), name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(template_name='userprofile/password_change_done.html'), name='password_change_done'),
    

    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='userprofile/password_reset_done.html'), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='userprofile/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='userprofile/password_reset_complete.html'), name='password_reset_complete'),

    path('myaccount/', views.myaccount, name='myaccount'),
    path('edit-account/', views.edit_account, name='edit_account'),
    path('my-store/', views.my_store, name='my_store'), 
    path('create-subscription/', views.create_subscription, name='create_subscription'),
    path('update_vendor_status/', views.update_vendor_status, name='update_vendor_status'),

    path('my-store/add-product/',views.add_product, name='add_product'),
    path('my-store/edit-product/<int:pk>/', views.edit_product, name='edit_product'),

    path('get-subcategories/', views.get_subcategories, name='get_subcategories'),
    
    path('my-store/delete-product/<int:pk>/',views.delete_product, name='delete_product'),
    path('vendors/<int:pk>/', views.vendor_detail, name='vendor_detail'),
]

#path('my-store/order-detail/<int:pk>/', views.my_store_order_detail, name='my_store_order_detail'),