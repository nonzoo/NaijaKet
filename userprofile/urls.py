from django.urls import path
from django.contrib.auth import views as auth_views
from . import views



urlpatterns = [
    path('privacy/', views.privacy, name='privacy'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.loginView ,name='login'),
    path('logout/', views.logoutUser, name='logout'),

    path('passwordchange/', auth_views.PasswordChangeView.as_view(template_name='userprofile/password_change_form.html'), name='password_change'),
    path('passwordchangedone/', auth_views.PasswordChangeDoneView.as_view(template_name='userprofile/password_change_done.html'), name='password_change_done'),
    

    path('passwordreset/', views.password_reset_request, name='password_reset'),
    path('passwordreset/done/', auth_views.PasswordResetDoneView.as_view(template_name='userprofile/password_reset_done.html'), name='password_reset_done'),
    path('passwordreset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='userprofile/password_reset_confirm.html'), name='password_reset_confirm'),
    path('passwordreset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='userprofile/password_reset_complete.html'), name='password_reset_complete'),

    path('myaccount/', views.myaccount, name='myaccount'),
    path('editaccount/', views.edit_account, name='edit_account'),
    path('mystore/', views.my_store, name='my_store'), 
    path('createsubscription/', views.create_subscription, name='create_subscription'),
    path('updatevendorstatus/', views.update_vendor_status, name='update_vendor_status'),

    path('mystore/addproduct/',views.add_product, name='add_product'),
    path('mystore/editproduct/<int:pk>/', views.edit_product, name='edit_product'),

    path('getsubcategories/', views.get_subcategories, name='get_subcategories'),
    
    path('mystore/deleteproduct/<int:pk>/',views.delete_product, name='delete_product'),
    path('vendors/<int:pk>/', views.vendor_detail, name='vendor_detail'),
]

#path('my-store/order-detail/<int:pk>/', views.my_store_order_detail, name='my_store_order_detail'),