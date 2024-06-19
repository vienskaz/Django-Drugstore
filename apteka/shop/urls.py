from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('account/login', views.login_view, name='login'),
    path('account/logout', views.logout_user, name="logout"),
    path('account/', views.Account.as_view(), name="account"),
    path('account/register', views.register_view, name="register"),
    path('products', views.ItemsView.as_view(), name='products'),
    path('<slug:slug>', views.SingleItem.as_view(), name="item-detail-page"),
    path('cart/', views.cart, name='cart'),
    path('update_item/', views.updateItem, name='update_item'),
    path('process_order/', views.processOrder, name='process_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('upload_prescription/', views.upload_prescription, name='upload_prescription'),
    path('download-csv/', views.download_csv, name='download_csv'),

]
