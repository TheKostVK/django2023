from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import Q
from django.views.generic import ListView
from .models import Product, Cart, CartItem, Category, Order


class ProductListView(View):
    def get(self, request):
        category_id = request.GET.get('category')
        categories = Category.objects.all()
        cart = Cart.objects.filter(user=request.user).order_by('-id').first()

        if category_id:
            products = Product.objects.filter(category_id=category_id)
        else:
            products = Product.objects.all()

        return render(request, 'shop/product/product_list.html', {
            'products': products,
            'categories': categories,
            'cart': cart,
        })

class SearchResultsView(ListView):
    model = Product
    template_name = 'shop/base/search_results.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct()

class ProductDetailView(View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)

        if request.user.is_authenticated:
            # Получаем последнюю корзину пользователя
            cart = Cart.objects.filter(user=request.user).order_by('-id').first()

            if not cart:
                if request.user.is_authenticated:
                    cart = Cart.objects.create(user=request.user)
                else:
                    session_key = request.session.session_key
                    if not session_key:
                        request.session.create()
                    cart = Cart.objects.create(session_key=request.session.session_key)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
            # Получаем последнюю корзину для текущей сессии
            cart = Cart.objects.filter(session_key=request.session.session_key).order_by('-id').first()

        product_in_cart = cart.items.filter(product=product).exists() if cart else False
        return render(request, 'shop/product/product_detail.html',
                      {'product': product, 'cart': cart, 'product_in_cart': product_in_cart})


class CartDetailView(View):
    def get(self, request):
        if request.user.is_authenticated:
            # Получаем последнюю корзину пользователя
            cart = Cart.objects.filter(user=request.user).order_by('-id').first()

            if not cart:
                if request.user.is_authenticated:
                    cart = Cart.objects.create(user=request.user)
                else:
                    session_key = request.session.session_key
                    if not session_key:
                        request.session.create()
                    cart = Cart.objects.create(session_key=request.session.session_key)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
            # Получаем последнюю корзину по session_key
            cart = Cart.objects.filter(session_key=request.session.session_key).order_by('-id').first()

        # Если корзина не найдена, создаём новую
        if not cart:
            cart = Cart.objects.create(user=request.user if request.user.is_authenticated else None,
                                       session_key=request.session.session_key)

        items = cart.items.all() if cart else []
        for item in items:
            item.total_price = item.quantity * item.product.price

        # Вычисляем общую стоимость всех товаров в корзине
        total_price = sum(item.total_price for item in items)

        return render(request, 'shop/cart/cart_detail.html', {'items': items, 'total_price': total_price})


# Класс для добавления товаров в корзину
class AddToCartView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            # Получаем последнюю корзину пользователя или создаём новую
            cart = Cart.objects.filter(user=request.user).order_by('-id').first()
            if not cart:
                cart = Cart.objects.create(user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
            # Получаем последнюю корзину для текущей сессии или создаём новую
            cart = Cart.objects.filter(session_key=request.session.session_key).order_by('-id').first()
            if not cart:
                cart = Cart.objects.create(session_key=request.session.session_key)

        # Добавляем товар в корзину
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect('cart')


# Класс для удаления товаров из корзины
class RemoveFromCartView(View):
    def post(self, request, product_id):
        if request.user.is_authenticated:
            # Получаем последнюю корзину пользователя
            cart = Cart.objects.filter(user=request.user).order_by('-id').first()
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
            # Получаем последнюю корзину для текущей сессии
            cart = Cart.objects.filter(session_key=request.session.session_key).order_by('-id').first()

        if not cart:
            return redirect('cart')

        # Удаляем товар из корзины
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()
        return redirect('cart')


class CreateOrderView(View):
    def post(self, request):
        if request.user.is_authenticated:
            # Получаем последнюю корзину пользователя
            cart = Cart.objects.filter(user=request.user).order_by('-id').first()
            if not cart:
                return redirect('cart')

            items = cart.items.all()

            if items:
                # Создаём заказ
                order = Order.objects.create(user=request.user, cart=cart)

                # Обновляем количество товаров на складе
                for item in items:
                    if item.product.stock >= item.quantity:
                        item.product.stock -= item.quantity
                        item.product.save()
                    else:
                        return redirect('cart')

                # Создаем новую корзину
                Cart.objects.create(user=request.user)

                return redirect('order_success')
            else:
                return redirect('cart')
        else:
            return redirect('login')


class OrderSuccessView(View):
    def get(self, request):
        return render(request, 'shop/order/order_success.html')

class UserOrdersView(LoginRequiredMixin, View):
    def get(self, request):
        # Получаем все заказы текущего пользователя
        orders = Order.objects.filter(user=request.user).order_by('-created_at')

        # Для каждого заказа вычисляем общую стоимость
        orders_with_totals = []
        for order in orders:
            total_price = sum(
                item.quantity * item.product.price for item in order.cart.items.all()
            )
            orders_with_totals.append({
                'order': order,
                'total_price': total_price,
            })

        return render(request, 'shop/order/user_orders.html', {'orders_with_totals': orders_with_totals})

class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Вычисляем данные для каждого товара
        items_with_totals = []
        for item in order.cart.items.all():
            total_price = item.quantity * item.product.price
            items_with_totals.append({
                'product': item.product,
                'quantity': item.quantity,
                'unit_price': item.product.price,
                'total_price': total_price,
            })

        # Общая стоимость заказа
        total_order_price = sum(item['total_price'] for item in items_with_totals)

        return render(request, 'shop/order/order_detail.html', {
            'order': order,
            'items_with_totals': items_with_totals,
            'total_order_price': total_order_price,
        })

class AdminOrderListView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff  # Ограничиваем доступ только для администраторов

    def get(self, request):
        orders = Order.objects.all().order_by('-created_at')

        # Рассчитываем общую стоимость для каждого заказа
        orders_with_totals = []
        for order in orders:
            total_price = sum(
                item.quantity * item.product.price for item in order.cart.items.all()
            )
            orders_with_totals.append({
                'order': order,
                'total_price': total_price,
            })

        return render(request, 'shop/admin/order_list.html', {
            'orders_with_totals': orders_with_totals,
        })


class AdminOrderUpdateView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Статус заказа №{order.id} был обновлён.")
        else:
            messages.error(request, "Некорректный статус.")

        return redirect('admin_orders')
