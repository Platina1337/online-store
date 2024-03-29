from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.views import View
from typing import Any
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from .models import Profile, BuildingMaterials
from decimal import Decimal
from django.conf import settings
from django.views.decorators.http import require_POST
from .forms import CartAddProductForm
from .cart import Cart

# Create your views here.

class ViewHome(ListView):
    model = BuildingMaterials
    template_name = 'blog/home.html'
    context_object_name = 'appoints'




class PostDetailView(DetailView):
    model = BuildingMaterials
    context_object_name = 'post'
    fields = ['title', 'content', 'image', 'price']
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        post_object = self.get_object()
        user = self.request.user

        context_data[self.context_object_name] = post_object
        return context_data

class ViewIndex(ListView):
    model = BuildingMaterials
    context_object_name = 'post'
    fields = ['title', 'content', 'image', 'price']
    template_name = 'blog/index.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        context['cart'] = cart
        return context

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(BuildingMaterials, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(BuildingMaterials=product,
                 quantity=cd['quantity'],
                 update_quantity=cd['update'])
    return redirect('index')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(BuildingMaterials, id=product_id)
    cart.remove(product)
    return redirect('index')



from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm
# Create your views here.



class RegistrationView(View):
    form_class = RegistrationForm
    template_name = 'blog/register.html'

    def get(self, request):
        form = self.form_class()
        print(request.POST)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        print(request.POST)
        if form.is_valid():
            print('Form is valid')
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Создание нового пользователя
            user = User.objects.create_user(username=username, email=email, password=password)

            # Сохранение пользователя в базе данных
            user.save()

            return redirect('login')  # Перенаправление на страницу с успехом
        else:
            print('Form is invalid')
            print(form.errors)
        return render(request, self.template_name, {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # Замените 'index' на имя вашего URL-шаблона

        # Обработка неверных учетных данных
        error_message = 'Invalid username or password'
        return render(request, 'blog/login.html', {'error_message': error_message})

    return render(request, 'blog/login.html')