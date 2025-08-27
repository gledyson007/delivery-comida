from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Cliente'),
        ('driver', 'Entregador'),
        ('owner', 'Dono de Restaurante'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="Função")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Telefone")

    def __str__(self):
        return self.username
    
class Restaurant(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant', verbose_name="Dono")
    name = models.CharField(max_length=100, verbose_name="Nome")
    address = models.CharField(max_length=255, verbose_name="Endereço")
    phone = models.CharField(max_length=15, verbose_name="Telefone")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    def __str__(self):
        return self.name
    
class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items', verbose_name="Restaurante")
    name = models.CharField(max_length=100, verbose_name="Nome do Item")
    description = models.CharField(blank=True, verbose_name="Descrição")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Preço")
    is_available = models.BooleanField(default=True, verbose_name="Disponivel")

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
    
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('in_progress', 'Em Preparo'),
        ('out_for_delivery', 'Saiu para a Entrega'),
        ('cancelled', 'Cancelado')
    )

    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders_as_customer', verbose_name="Cliente")
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_driver', verbose_name="Entregador")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders', verbose_name="Restaurante")

    items = models.ManyToManyField(MenuItem, through='OrderItem', verbose_name="Itens de Pedido")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Total")
    delivery_address = models.CharField(max_length=255, verbose_name="Endereço de Entrega")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="Atualizado em")

    def __str__(self):
        return f"Pedido #{self.id} - {self.customer.username}"
    
class OrderItem(models.Model):
    """
    Este é um modelo 'through' (através). Ele nos permite guardar informações
    extras na relação entre um Pedido e um Item de Cardápio, como a quantidade.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantidade")

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} no Pedido #{self.order.id}"
