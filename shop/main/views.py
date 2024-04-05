from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from typing import Any

from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from .models import BuildingMaterials, Review
from django.views.decorators.http import require_POST
from cart.forms import CartAddProductForm

def product_detail(request, id, slug):
    # Получаем продукт (пост) по id и slug
    product = get_object_or_404(BuildingMaterials, id=id, slug=slug, available=True)
    reviews = Review.objects.filter(post=product)
    # Форма для добавления продукта в корзину
    cart_product_form = CartAddProductForm()

    # Проверяем метод запроса
    if request.method == 'POST':
        if request.user.is_authenticated:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                # Создаем объект отзыва, связываем с продуктом и текущим пользователем
                review = review_form.save(commit=False)
                review.post = product
                review.author = request.user  # Устанавливаем текущего пользователя как автора отзыва
                review.save()
                # Опциональное сообщение об успешном добавлении отзыва
                # Можно добавить сообщение об успешном добавлении отзыва
                return redirect('main:post-detail', id=id, slug=slug)  # Перенаправляем обратно на страницу продукта

    else:
        review_form = ReviewForm()

    # Отображаем шаблон с информацией о продукте, формой для корзины и формой для отзыва
    return render(request, 'blog/post_detail.html', {
        'product': product,
        'cart_product_form': cart_product_form,
        'review_form': review_form,
        'reviews': reviews  # Передаем список отзывов в контекст шаблона
    })





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

from django.shortcuts import redirect


import requests
from django.http import JsonResponse

import requests




from rest_framework.decorators import api_view

@api_view(['POST'])
def import_contacts_and_send_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Параметры для добавления в список Unisender
        api_key = '6tn47mrmxx76i9ooh4mbb8uwezrufedg34xk9kxo'
        list_id = '1'  # ID вашего списка в Unisender

        # Добавляем контакт в список Unisender
        import_url = f'https://api.unisender.com/ru/api/importContacts?format=json&api_key={api_key}&field_names[0]=email&field_names[1]=email_list_ids&data[0][0]={email}&data[0][1]={list_id}'
        import_response = requests.post(import_url)

        if import_response.status_code == 200:
            import_data = import_response.json()
            if 'error' in import_data:
                return JsonResponse({"error": "Произошла ошибка при добавлении контакта: " + import_data['error']},
                                    status=400)

            # Контакт успешно добавлен, отправляем ему письмо
            send_email_url = 'https://api.unisender.com/ru/api/sendEmail'
            send_email_payload = {
                'api_key': api_key,
                'sender_name': 'Гоген Солнцев',
                'sender_email': 'bbd3372005@gmail.com',
                'subject': 'СКИДКИ 10000%, ВСЕ БЕСПЛАТНО!!!',
                'body': '<html><body><h1>СКИДОК НЕТ ЛОШОК</h1></body></html>',
                'list_id': list_id,
                'email': email
            }
            send_email_response = requests.post(send_email_url, data=send_email_payload)

            if send_email_response.status_code == 200:
                send_email_data = send_email_response.json()
                if 'error' in send_email_data:
                    return JsonResponse({"error": "Произошла ошибка при отправке письма: " + send_email_data['error']},
                                        status=400)
                return redirect('main:index')  # Перенаправление на страницу успеха
            else:
                return JsonResponse({"error": "Ошибка при отправке письма."}, status=send_email_response.status_code)
        else:
            return JsonResponse({"error": "Произошла ошибка при добавлении контакта."},
                                status=import_response.status_code)
    else:
        return JsonResponse({"error": "Метод не поддерживается."}, status=405)



def logout_user(reqest):
    logout(reqest)
    return redirect('main:index')
# Create your views here.
from django.http import HttpResponseForbidden

def csrf_failure(request, reason=""):
    # Ваша логика обработки ошибки CSRF
    return HttpResponseForbidden('CSRF verification failed. Please try again.')


class ViewHome(ListView):
    model = BuildingMaterials

    template_name = 'blog/home.html'
    context_object_name = 'appoints'





class ViewIndex(ListView):
    model = BuildingMaterials
    context_object_name = 'post'
    fields = ['title', 'content', 'image', 'price']
    template_name = 'blog/index.html'
    paginate_by = 9

    def get_queryset(self):
        # Получаем queryset всех объектов BuildingMaterials
        queryset = super().get_queryset()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем объекты для текущей страницы с помощью пагинатора
        page_objects = context['post']
        paginator = Paginator(page_objects, self.paginate_by)

        # Получаем номер текущей страницы из GET-параметра 'page'
        page_number = self.request.GET.get('page')
        page_objects = paginator.get_page(page_number)

        # Обновляем контекст данных для передачи объектов текущей страницы
        context['post'] = page_objects
        return context


from django.shortcuts import render, redirect
from .forms import RegistrationForm, ReviewForm


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

            return redirect('main:login')  # Перенаправление на страницу с успехом
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
            return redirect('main:index')  # Замените 'index' на имя вашего URL-шаблона

        # Обработка неверных учетных данных
        error_message = 'Invalid username or password'
        return render(request, 'blog/login.html', {'error_message': error_message})

    return render(request, 'blog/login.html')