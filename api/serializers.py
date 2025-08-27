from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import User, Restaurant, MenuItem, Order, OrderItem

class UserRegistrationSerializer(serializers.ModelSerializer):
    # Usamos CharField com write_only=True para a senha,
    # para que ela seja usada na criação mas não seja exibida nas respostas da API.
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        # Campos que serão usados para o cadastro.
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'role', 'phone_number')

    def create(self, validated_data):
        # Este método é chamado quando .save() é executado na view.
        # Usamos create_user para garantir que a senha seja "hasheada" (criptografada).
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data['role'],
            phone_number=validated_data.get('phone_number')
        )
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number')
        read_only_fields = ('username', 'role')

class RestaurantSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Restaurant
        fields = ('id', 'owner', 'name', 'address', 'phone', 'is_active')

class MenuItemSerializer(serializers.ModelSerializer):
    restaurant = serializers.ReadOnlyField(source='restaurant.name')

    class Meta:
        model = MenuItem
        fields = ('id', 'restaurant', 'name', 'description', 'price', 'is_available')

class OrderItemCreateSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())

    class Meta:
        model = OrderItem
        fields = ('menu_item', 'quantity')


# 2. Serializer para CRIAR o pedido (só para INPUT)
class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ('restaurant', 'delivery_address', 'items')

    def create(self, validated_data):
        customer = self.context['request'].user
        items_data = validated_data.pop('items')
        restaurant = validated_data['restaurant']

        with transaction.atomic():
            total_price = 0
            for item_data in items_data:
                menu_item = item_data['menu_item']
                if menu_item.restaurant != restaurant:
                    raise ValidationError(f"O item '{menu_item.name}' não pertence ao restaurante '{restaurant.name}'.")
                total_price += menu_item.price * item_data['quantity']
            
            order = Order.objects.create(
                customer=customer,
                total_price=total_price,
                **validated_data
            )

            for item_data in items_data:
                OrderItem.objects.create(
                    order=order,
                    menu_item=item_data['menu_item'],
                    quantity=item_data['quantity']
                )
            return order

# 3. Serializer para EXIBIR um item com detalhes (usado dentro do OrderDisplaySerializer)
class OrderItemDisplaySerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer()

    class Meta:
        model = OrderItem
        fields = ('menu_item', 'quantity')

# 4. Serializer para EXIBIR um pedido completo (só para OUTPUT)
class OrderDisplaySerializer(serializers.ModelSerializer):
    items = OrderItemDisplaySerializer(many=True, source='orderitem_set')
    customer = serializers.ReadOnlyField(source='customer.username')
    restaurant = RestaurantSerializer()

    class Meta:
        model = Order
        fields = ('id', 'customer', 'restaurant', 'items', 'status', 'total_price', 'delivery_address', 'created_at')

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status',]

class LocationSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()    