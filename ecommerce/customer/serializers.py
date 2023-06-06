from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from .models import CustomerAccount, Address, ProductCategory, Product, ProductImage


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class CustomerAccountSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    address = AddressSerializer(required=False)

    class Meta:
        model = CustomerAccount
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'address']

    def update(self, instance, validated_data):
        customer_data = self.context.get('request_data')['customer']
        address_data = validated_data.pop('address', None)

        for field in self.Meta.fields:
            if field in customer_data and customer_data[field] != getattr(instance, field):
                setattr(instance, field, customer_data[field])

        if address_data:
            address_serializer = self.fields['address']
            address_instance = instance.address

            if address_instance:
                address_serializer.update(address_instance, address_data)
            else:
                address_instance = address_serializer.create(address_data)
                instance.address = address_instance

        instance.save()
        return instance


class CustomerSerializer(serializers.Serializer):
    customer = CustomerAccountSerializer(required=True)
    address = AddressSerializer(required=True)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    product_category = PrimaryKeyRelatedField(queryset=ProductCategory.objects.all())
    image_serializer = serializers.ImageField(required=False)
    product_image = ProductImageSerializer(required=False)

    class Meta:
        model = Product
        fields = ['id', 'product_owner', 'product_name', 'product_description', 'product_category',
                  'product_price', 'product_quantity', 'slug', 'created_time', 'product_image', 'updated_time',
                  'image_serializer']
        extra_kwargs = {
            "slug": {'required': False}
        }

    def update(self, instance, validated_data):
        product_image = validated_data.pop('image_serializer', None)
        instance = super().update(instance, validated_data)
        if product_image:
            ProductImage.objects.filter(product_images__id=instance.id).update(image=product_image)
        return instance


class ProductDetailSerializer(serializers.Serializer):
    product = ProductSerializer(required=True)
    image = ProductImage()
    category = ProductCategory()
