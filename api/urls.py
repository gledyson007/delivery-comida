# api/urls.py

from django.urls import path
from .views import (
    UserRegistrationView, UserProfileView,
    RestaurantListCreateView, RestaurantDetailView,
    MenuItemListCreateView, MenuItemDetailView, PublicRestaurantListView, PublicRestaurantMenuView, OrderListCreateView, RestaurantOrderListView,
    RestaurantOrderDetailView, AvailableOrdersListView, DriverClaimOrderView, DriverLocationUpdateView, CustomerTrackOrderView # Importe as novas views
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # URLs de Autenticação e Perfil
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # URLs para Donos de Restaurante (Gerenciamento)
    path('restaurants/', RestaurantListCreateView.as_view(), name='restaurant-list-create'),
    path('restaurants/<int:pk>/', RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('restaurants/<int:restaurant_pk>/menu/', MenuItemListCreateView.as_view(), name='menu-item-list-create'),
    path('restaurants/<int:restaurant_pk>/menu/<int:item_pk>/', MenuItemDetailView.as_view(), name='menu-item-detail'),

    # URLs Públicas para Clientes
    path('public/restaurants/', PublicRestaurantListView.as_view(), name='public-restaurant-list'),
    path('public/restaurants/<int:restaurant_pk>/menu/', PublicRestaurantMenuView.as_view(), name='public-restaurant-menu'),
    # URL de Pedidos
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),

    # URLs para Gerenciamento de Pedidos (Dono do Restaurante)
    path('restaurant/orders/', RestaurantOrderListView.as_view(), name='restaurant-order-list'),
    path('restaurant/orders/<int:pk>/', RestaurantOrderDetailView.as_view(), name='restaurant-order-detail'),

    # URLs para a Visão do Entregador
    path('driver/available-orders/', AvailableOrdersListView.as_view(), name='driver-available-orders'),
    path('driver/claim-order/<int:pk>/', DriverClaimOrderView.as_view(), name='driver-claim-order'),

     # URLs de Rastreamento em Tempo Real
    path('driver/orders/<int:pk>/location/', DriverLocationUpdateView.as_view(), name='driver-update-location'),
    path('customer/orders/<int:pk>/track/', CustomerTrackOrderView.as_view(), name='customer-track-order'),
]
