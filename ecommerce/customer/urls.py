from django.urls import path

from .views import CustomerList, CustomerDetails, ProductListCreateView, ProductRetrieveUpdateDestroyView

urlpatterns = [
    path('create-or-get-customer/', CustomerList.as_view(), name='create-or-get-customer-list'),
    path(f'update-or-delete-customer/<int:user_id>', CustomerDetails.as_view(), name='update-or-delete-customer'),
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-retrieve-update-destroy')
]
