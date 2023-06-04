from django.http import Http404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView, status

from .models import CustomerAccount, Address, Product, ProductCategory, ProductImage
from .pagination import CustomerListPagination
from .serializers import CustomerSerializer, CustomerAccountSerializer, ProductSerializer


def get_object(user_id: int):
    try:
        return CustomerAccount.objects.get(pk=user_id)
    except CustomerAccount.DoesNotExist:
        raise Http404


class CustomerList(APIView):
    serializer_class = CustomerSerializer
    pagination_class = CustomerListPagination

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            customer_data = data_dict['customer']
            address_data = data_dict['address']
            username, email, password, first_name, last_name = customer_data.values()
            street, state, city, country, postal_code = address_data.values()
            address_obj = Address.objects.create(street=street, state=state, city=city,
                                                 postal_code=postal_code, country=country)
            CustomerAccount.objects.create_user(address=address_obj, email=email, username=username,
                                                password=password, first_name=first_name, last_name=last_name)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        customers = CustomerAccount.objects.all()
        paginator = self.pagination_class()
        paginated_customer = paginator.paginate_queryset(customers, request)
        serializer = CustomerAccountSerializer(paginated_customer, many=True)
        return paginator.get_paginated_response(serializer.data)


class CustomerDetails(APIView):

    def patch(self, request, user_id: int):
        customer = get_object(user_id)
        serializer = CustomerAccountSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id: int):
        customer = get_object(user_id)
        customer.delete()
        return Response(status=status.HTTP_200_OK)


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductListCreateView(APIView):
    serializer_class = ProductSerializer

    pagination_class = CustomerListPagination

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            print(data_dict)
            product_owner = data_dict['product_owner']
            product_name = data_dict['product_name']
            product_description = data_dict['product_description']
            product_price = data_dict['product_price']
            product_quantity = data_dict['product_quantity']
            product_category = data_dict['product_category']['name']
            # product_image = data_dict['product_images']['image']
            try:
                product_category = ProductCategory.objects.get(name=product_category)

                user = get_object(product_owner)
                product_obj = Product.objects.create(product_owner=user, product_name=product_name,
                                                     product_quantity=product_quantity,
                                                     product_description=product_description,
                                                     product_price=product_price,
                                                     product_category=product_category,
                                                     is_active=True)
                product_obj.save()
                # ProductImage.objects.create(product=product_obj, image=product_image)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ProductCategory.DoesNotExist:
                raise Http404
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        products = Product.objects.all()
        paginator = self.pagination_class()
        paginated_customer = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(paginated_customer, many=True)
        return paginator.get_paginated_response(serializer.data)
