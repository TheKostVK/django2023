from django.urls import path
from .views import ProductListView, ProductDetailView, RemoveFromCartView, CartDetailView, AddToCartView, \
    CreateOrderView, OrderSuccessView, UserOrdersView, OrderDetailView, AdminOrderListView, AdminOrderUpdateView, \
    SearchResultsView

urlpatterns = [
    path('', ProductListView.as_view(), name='shop'),
    path('product/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('cart/', CartDetailView.as_view(), name='cart'),
    path('add-to-cart/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:product_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('create_order/', CreateOrderView.as_view(), name='create_order'),
    path('order_success/', OrderSuccessView.as_view(), name='order_success'),
    path('orders/', UserOrdersView.as_view(), name='user_orders'),
    path('orders/<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('admin/orders/', AdminOrderListView.as_view(), name='admin_orders'),
    path('admin/orders/<int:order_id>/update/', AdminOrderUpdateView.as_view(), name='admin_order_update'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
]