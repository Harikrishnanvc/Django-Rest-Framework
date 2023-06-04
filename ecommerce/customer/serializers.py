from rest_framework import serializers

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
        address_data = validated_data.pop('address', None)
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
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
    product_category = ProductCategorySerializer()
    product_images = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'product_owner', 'product_name', 'product_description', 'product_category',
                  'product_price', 'product_quantity', 'slug', 'is_active', 'created_time',
                  'updated_time', 'product_images']
        extra_kwargs = {
            "slug": {'required': False},
        }

    def update(self, instance, validated_data):
        category_data = validated_data.pop('product_category')
        images_data = validated_data.pop('product_images')
        category = instance.product_category
        category.name = category_data.get('name', category.name)
        category.is_active = category_data.get('is_active', category.is_active)
        category.save()
        instance.product_name = validated_data.get('product_name', instance.product_name)
        instance.product_description = validated_data.get('product_description', instance.product_description)
        instance.product_price = validated_data.get('product_price', instance.product_price)
        instance.product_quantity = validated_data.get('product_quantity', instance.product_quantity)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        existing_images = list(instance.product_images.all())
        for image_data in images_data:
            image_id = image_data.get('id')
            if image_id:
                image = existing_images.pop(existing_images.index(ProductImage.objects.get(id=image_id)))
                image.image = image_data.get('image', image.image)
                image.save()
            else:
                ProductImage.objects.create(product=instance, **image_data)

        for image in existing_images:
            image.delete()

        return instance


class ProductDetailSerializer(serializers.Serializer):
    product = ProductSerializer(required=True)
    image = ProductImage()
    category = ProductCategory()
