from django.contrib import admin
from django import forms
from .models import Category, Product, ProductCharacteristic, Cart, CartItem, Order


# Inline для характеристик
class ProductCharacteristicInline(admin.TabularInline):
    model = ProductCharacteristic
    extra = 1

# Админка для категории
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Админка для продукта
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name',)
    inlines = [ProductCharacteristicInline]  # Подключаем Inline

# Элементы корзины
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

# Модель корзины
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key')
    inlines = [CartItemInline]
    search_fields = ('user__username', 'session_key')

# Модель заказов
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'cart', 'status')  # Используем добавленные поля
    search_fields = ('user__username', 'cart__user__username', 'status')