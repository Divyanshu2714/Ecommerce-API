from rest_framework import serializers

from api.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_price',
            'quantity',
            'subtotal',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'product_name',
            'product_price',
            'subtotal',
            'created_at',
        ]
    def validate_quantity(self,value):
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be grater than 0"
            )
        return value

    def get_subtotal(self, obj):
        return obj.product.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id',
            'items',
            'total_amount',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'items',
            'total_amount',
            'created_at',
            'updated_at',
        ]

    def get_total_amount(self, obj):
        total = 0
        for item in obj.items.all():
            total += item.product.price * item.quantity
        return total


