from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView as SimpleJWTTokenObtainPairView
from api.models import Cart, CartItem, Category, Product, Order, OrderItem
from api.serializers.cart import CartItemSerializer, CartSerializer
from api.serializers.product import CategorySerializer, ProductSerializer
from api.serializers.order import OrderSerializer
from .permissions import IsAdminUser
from .serializers.auth import RegisterSerializer
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from api.filters import Productfilter
from api.pagination import ProductPagination
from api.order_status import is_valid_transaction


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    with transaction.atomic():
        cart = get_object_or_404(
            Cart.objects.prefetch_related('items__product'),
            user=request.user,
        )
        cart_items = list(cart.items.all())

        if not cart_items:
            return Response(
                {"error": "Your cart is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product_ids = [item.product_id for item in cart_items]
        locked_products = {
            product.id: product
            for product in Product.objects.select_for_update().filter(id__in=product_ids)
        }

        for cart_item in cart_items:
            product = locked_products.get(cart_item.product_id)

            if not product or not product.is_active:
                return Response(
                    {"error": f"product '{cart_item.product.name}' is no longer available"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if cart_item.quantity > product.stock:
                return Response(
                    {
                        "error": (
                            f"Insufficient stock for '{product.name}'. "
                            f"Available: {product.stock}"
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        order = Order.objects.create(
            user=request.user,
            status=Order.OrderStatus.PENDING,
            total_amount=0,
        )

        total_amount = 0

        for cart_item in cart_items:
            product = locked_products[cart_item.product_id]
            price = product.price
            quantity = cart_item.quantity
            subtotal = price * quantity

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price,
            )
            product.stock -= quantity
            product.save(update_fields=['stock'])
            total_amount += subtotal

        order.total_amount = total_amount
        order.save(update_fields=['total_amount'])
        cart.items.all().delete()

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_details(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id,
        user=request.user,
    )
    serializer = OrderSerializer(order)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    new_status = request.data.get('status')

    valid_statuses = [
        choice[0] 
        for choice in Order.OrderStatus.choices
    ]

    if new_status not in valid_statuses:
        return Response(
            {
                "error": "Invalid order status",
                "allowed_status": valid_statuses,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not is_valid_transaction(
        order.status,
        new_status
    ):
        return Response(
            {
                "error": (
                    f"Cannot change order status "
                    f"from {order.status} "
                    f"to {new_status}."
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    order.status = new_status
    order.save(update_fields=['status', 'updated_at'])
    serializer = OrderSerializer(order)
    return Response(serializer.data)


class CustomTokenObtainPairView(SimpleJWTTokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.status_code = status.HTTP_201_CREATED
        return response


@api_view(['GET'])
def home(request):
    return Response({
        "message": "E-commerce API is running successfully!",
        "status": "success",
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_test(request):
    return Response({
        "message": "Welcome Admin!",
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_cart(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart_obj)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    product_id = request.data.get('product')
    quantity = request.data.get('quantity', 1)

    if product_id in (None, ''):
        return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        return Response({"error": "Product ID must be a valid number"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response({"error": "Quantity must be a valid number"}, status=status.HTTP_400_BAD_REQUEST)

    if quantity <= 0:
        return Response({"error": "Quantity must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    if quantity > product.stock:
        return Response({"error": "Requested quantity exceeds available stock"}, status=status.HTTP_400_BAD_REQUEST)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if item_created:
        cart_item.quantity = quantity
    else:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            return Response({"error": "Total quantity exceeds available stock"}, status=status.HTTP_400_BAD_REQUEST)
        cart_item.quantity = new_quantity

    cart_item.save()
    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.select_related('product', 'cart').get(
            id=item_id,
            cart__user=request.user,
        )
    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

    quantity = request.data.get('quantity')

    if quantity is None:
        return Response({"error": "Quantity is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response({"error": "Quantity must be a valid number"}, status=status.HTTP_400_BAD_REQUEST)

    if quantity <= 0:
        return Response({"error": "Quantity must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

    if quantity > cart_item.product.stock:
        return Response({"error": "Requested quantity exceeds available stock"}, status=status.HTTP_400_BAD_REQUEST)

    cart_item.quantity = quantity
    cart_item.save()

    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

    cart_item.delete()
    return Response({"message": "Item removed from the cart"}, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        'category'
    ).all()
    serializer_class = ProductSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_class = Productfilter

    search_fields = [
        'name',
        'description',
        'category__name'
    ]

    ordering_fields = [
        'name',
        'price',
        'stock',
        'created_at'
    ]

    ordering = [
        '-created_at'
    ]

    pagination_class = ProductPagination

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]