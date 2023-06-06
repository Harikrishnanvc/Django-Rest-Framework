from django.http import Http404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView, status

from .models import CustomerAccount, Address, Product, ProductImage
from .pagination import CustomerListPagination
from .serializers import CustomerSerializer, CustomerAccountSerializer, ProductSerializer, ProductImageSerializer


def get_object(user_id: int):
    try:
        return CustomerAccount.objects.get(pk=user_id)
    except CustomerAccount.DoesNotExist:
        raise Http404("Customer does not exist")


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
        serializer = CustomerAccountSerializer(customer, data=request.data, partial=True,
                                               context={'request_data': request.data})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id: int):
        customer = get_object(user_id)
        customer.delete()
        return Response("Deleted Customer Successfully", status=status.HTTP_200_OK)


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


#   TODO: While adding multiple images use slug(same slug for multiple images to filter those things)
class ProductListCreateView(APIView):
    serializer_class = ProductSerializer
    pagination_class = CustomerListPagination

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'context': request.data})
        if serializer.is_valid():
            image_list = request.FILES.getlist('product_image')
            serializer.save()
            for image in image_list:
                product_image_serializer = ProductImageSerializer(data={'image': image})
                if product_image_serializer.is_valid():
                    product_image_serializer.save()
                    serializer.product_image = product_image_serializer.data['id']
                    image_id = product_image_serializer.data['id']
                    product_image = ProductImage.objects.get(id=image_id)
                    Product.objects.filter(id=serializer.data['id']).update(product_image=product_image)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        products = Product.objects.all()
        paginator = self.pagination_class()
        paginated_customer = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(paginated_customer, many=True)
        return paginator.get_paginated_response(serializer.data)
