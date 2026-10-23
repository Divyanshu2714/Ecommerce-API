from rest_framework import serializers

from api.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]
    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "category name cannot be empty"
            )
        return value


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.name',
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock',
            'category',
            'category_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'category_name',
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Product name cannot be empty."
            )
        if len(value) < 2:
            raise serializers.ValidationError(
                "Product name must conatins atleast 2 characters"
            )
        return value

    def validate_price(self, value):
        if value <=0:
            raise serializers.ValidationError(
                "Price must be grater than 0"
            )
        return value
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Stock cannot be negative"
            )
        return value