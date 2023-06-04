import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import slugify


# Create your models here.
class Address(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.postal_code}, {self.country}"

    class Meta:
        verbose_name_plural = 'Address'


class CustomerAccount(AbstractUser):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    username = models.CharField(max_length=60, unique=True)
    password = models.CharField(max_length=150)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True)
    created_time = models.DateField(verbose_name='created time', auto_now_add=True)
    updated_time = models.DateField(verbose_name='updated time', auto_now=True)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return self.last_name + ' ' + self.first_name

    @property
    def get_address(self):
        return self.address

    class Meta:
        verbose_name_plural = 'Customer Account'


class ProductCategory(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Product Category"

    def __str__(self):
        return self.name


class Product(models.Model):
    product_owner = models.ForeignKey(CustomerAccount, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=50)
    product_description = models.TextField()
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_quantity = models.PositiveIntegerField()
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=False)
    end_date = models.DateField(null=True)
    start_date = models.DateField(auto_now_add=True, null=True)
    created_time = models.DateField(verbose_name='created time', auto_now_add=True)
    updated_time = models.DateField(verbose_name='updated time', auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        if Product.objects.filter(slug=self.slug).exists():
            self.end_date = self.start_date + timedelta(days=60)
            self.slug = f"{self.slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"
