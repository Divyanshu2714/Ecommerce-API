from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length = 100, unique = True)
    description = models.TextField(blank = True)

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name= models.CharField(max_length = 200)
    description = models.TextField(blank = True)

    price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2
    )

    stock = models.PositiveIntegerField(default = 0)

    category = models.ForeignKey(
        Category,
        on_delete = models.CASCADE,
        related_name = 'products'
    )

    is_active = models.BooleanField(default = True)

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(
        'auth.User',
        on_delete = models.CASCADE,
        related_name = 'cart'
    )

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f"Cart - {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete = models.CASCADE,
        related_name = 'items'
    )

    product = models.ForeignKey(
        Product,
        on_delete = models.CASCADE
    )

    quantity = models.PositiveIntegerField(default = 1)

    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = "CONFIRMED", 'Confirmed'
        PROCESSING = "PROCESSING", 'Processing'
        SHIPPED = "SHIPPED", 'Shipped'
        DELIVERED = "DELIVERED", 'Delivered'
        CANCELED = "CANCELED", 'Canceled'

    user = models.ForeignKey(
        'auth.User',
        on_delete = models.CASCADE,
        related_name = 'orders'
    )

    status = models.CharField(
        max_length = 20,
        choices = OrderStatus.choices,
        default = OrderStatus.PENDING
    )

    total_amount = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        default = 0
    )

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete = models.CASCADE,
        related_name = 'items'
    )

    product = models.ForeignKey(
        Product,
        on_delete = models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2
    )

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"