from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.custom_login, name='login'),  # Login page as root
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete-sheet/<int:sheet_id>/', views.delete_sheet, name='delete_sheet'),
    path('create-sheet/', views.create_sheet, name='create_sheet'),
    path('sheet/<int:sheet_id>/', views.view_sheet, name='view_sheet'),
    path('sheet/<int:sheet_id>/add-product/', views.add_product, name='add_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('update-invoice-meta/<int:sheet_id>/', views.update_invoice_meta, name='update_invoice_meta'),
    path('update-customer-info/<int:sheet_id>/', views.update_customer_info, name='update_customer_info'),
    path('generate-invoice/<int:sheet_id>/', views.generate_invoice, name='generate_invoice'),
    path('about/', views.about, name='about'),
]

