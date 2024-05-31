from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView

from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from main.models import Profile

# Create your views here.
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'],
                                         profile=request.user.profile)
            # очистка корзины
            cart.clear()
            return render(request, 'orders/order/created.html',
                          {'order': order})
    else:
        form = OrderCreateForm
    return render(request, 'orders/order/create.html',
                  {'cart': cart, 'form': form})

class UserOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order/orders_view.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(items__profile=self.request.user.profile).distinct()

