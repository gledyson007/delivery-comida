import os
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from .permissions import IsRestauranteOwner, IsCustomer, IsDriver
from .serializers import UserRegistrationSerializer, UserProfileSerializer, RestaurantSerializer, MenuItemSerializer, OrderCreateSerializer, OrderDisplaySerializer, OrderStatusUpdateSerializer
from .models import User, Restaurant, MenuItem, Order
from firebase_admin import db
from .serializers import LocationSerializer

class UserRegistrationView(generics.CreateAPIView):
    """
    View para registrar um novo usuário.
    Acessível via POST para /api/register/
    """
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # is_valid() irá validar os dados. Se algo estiver errado (ex: email inválido),
        # ele irá automaticamente retornar uma resposta de erro 400.
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Resposta customizada de sucesso.
        response_data = {
            "message": "Usuário registrado com sucesso!",
            "user_id": serializer.instance.id,
            "username": serializer.instance.username
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
class RestaurantListCreateView(generics.ListCreateAPIView):
    serializer_class = RestaurantSerializer
    permission_classes = [IsRestauranteOwner]

    def get_queryset(self):
        # Retorna apenas restaurante ligado ao dono
        # E um dono so pode ter um restaurante(OneToOneField)
        return Restaurant.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        # Associa o dono do restaurante ao usuário que está fazendo a requisição.
        serializer.save(owner=self.request.user)

class RestaurantDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = RestaurantSerializer
    permission_classes = [IsRestauranteOwner]

    def get_queryset(self):
        return Restaurant.objects.filter(owner=self.request.user)
    
class MenuItemListCreateView(generics.ListCreateAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [IsRestauranteOwner]

    def get_queryset(self):
        restaurant_pk = self.kwargs['restaurant_pk']
        return MenuItem.objects.filter(restaurant__pk=restaurant_pk)
    
    def perform_create(self, serializer):
        restaurant_pk = self.kwargs['restaurant_pk']
        restaurant = get_object_or_404(Restaurant, pk=restaurant_pk, owner=self.request.user)
        serializer.save(restaurant=restaurant)


class MenuItemDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [IsRestauranteOwner]

    def get_queryset(self):
        restaurant_pk = self.kwargs['restaurant_pk']
        return MenuItem.objects.filter(restaurant__pk=restaurant_pk, restaurant__owner=self.request.user)
    
    def get_object(self):
        queryset = self.get_queryset()
        item_pk = self.kwargs['item_pk']
        obj = get_object_or_404(queryset, pk=item_pk)
        return obj
    
class PublicRestaurantListView(generics.ListAPIView):
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Restaurant.objects.filter(is_active=True)
    
class PublicRestaurantMenuView(generics.ListAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        restaurant_pk = self.kwargs['restaurant_pk']
        return MenuItem.objects.filter(restaurant__pk=restaurant_pk, is_available=True)
    
class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderDisplaySerializer
        
        return OrderCreateSerializer
    
    def create(self, request, *args, **kwargs):
        # 1. Pegue a CLASSE do serializer de criação
        serializer_class = self.get_serializer_class()
        
        # 2. Crie a INSTÂNCIA do serializer, passando os dados e o contexto
        context = self.get_serializer_context()
        create_serializer = serializer_class(data=request.data, context=context)
        
        create_serializer.is_valid(raise_exception=True)
        order = create_serializer.save()

        # Crie a resposta usando o serializer de exibição
        display_serializer = OrderDisplaySerializer(order, context=context)
        headers = self.get_success_headers(display_serializer.data)
        return Response(display_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class RestaurantOrderListView(generics.ListAPIView):
    serializer_class = OrderDisplaySerializer
    permission_classes = [IsAuthenticated, IsRestauranteOwner]

    def get_queryset(self):
        return Order.objects.filter(restaurant__owner=self.request.user).order_by('-created_at')
    
class RestaurantOrderDetailView(generics.UpdateAPIView):
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsRestauranteOwner]

    def get_queryset(self):
        return Order.objects.filter(restaurant__owner=self.request.user)

class AvailableOrdersListView(generics.ListAPIView):
    serializer_class = OrderDisplaySerializer
    permission_classes = [IsAuthenticated, IsDriver]

    def get_queryset(self):
        return Order.objects.filter(status='out_for_delivery', driver=None).order_by('created_at')

class DriverClaimOrderView(generics.UpdateAPIView):
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsDriver]
    lookup_field = 'pk'

    def get_queryset(self):
        return Order.objects.filter(status='out_for_delivery', driver=None)
    
    def perform_create(self, serializer):
        order = self.get_object()
        if order.driver is not None:
            raise ValidationError("Este pedido já foi aceito por outro entregador.")
        
        serializer.instance.driver = self.request.user
        serializer.save()

class DriverLocationUpdateView(generics.UpdateAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated, IsDriver]

    def update(self, request, *args, **kwargs):
        order_id = self.kwargs.get('pk')
        try:
            order = Order.objects.get(pk=order_id, driver=self.request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Pedido não encontrado ou não pertence a você."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        location_data = serializer.validated_data

        ref = db.reference(f'/order_locations/{order_id}')
        ref.set({
            'lat': location_data['lat'],
            'lng': location_data['lng'],
            'driver_id': self.request.user.id
        })

        return Response({"status": "localização atualizada com sucesso"}, status=status.HTTP_200_OK)
    
class CustomerTrackOrderView(generics.RetrieveAPIView):
    """
    View para o cliente obter as informações para rastrear um pedido.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request, *args, **kwargs):
        order_id = self.kwargs.get('pk')
        try:
            # Garante que o cliente só pode rastrear seus próprios pedidos.
            Order.objects.get(pk=order_id, customer=self.request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Pedido não encontrado ou não pertence a você."}, status=status.HTTP_404_NOT_FOUND)

        # Em um projeto real, aqui você geraria um token customizado do Firebase
        # e o enviaria para o cliente.
        # Por agora, apenas confirmamos o acesso.

        firebase_db_url = os.getenv("FIREBASE_DATABASE_URL")
        firebase_path = f"/order_locations/{order_id}"

        return Response({
            "message": "Acesso permitido. Ouça por atualizações no caminho especificado.",
            "firebase_database_url": firebase_db_url,
            "firebase_path": firebase_path
        }, status=status.HTTP_200_OK)