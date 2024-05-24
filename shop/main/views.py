from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from typing import Any

from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, UpdateView
from .models import BuildingMaterials, Review, Like, Profile, Category
from django.views.decorators.http import require_POST
from cart.forms import CartAddProductForm
from news.models import Video
from orders.models import OrderItem

def product_detail(request, id, slug):
    product = get_object_or_404(BuildingMaterials, id=id, slug=slug, available=True)
    reviews = Review.objects.filter(post=product)

    # Pagination - Show 4 reviews per page
    paginator = Paginator(reviews, 4)
    page_number = request.GET.get('page')  # Get the current page number
    try:
        reviews = paginator.page(page_number)
    except PageNotAnInteger:
        reviews = paginator.page(1)  # If page is not an integer, deliver first page
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page

    cart_product_form = CartAddProductForm()

    if request.method == 'POST':
        if request.user.is_authenticated:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.post = product
                review.author = request.user
                review.save()
                return redirect('main:post-detail', id=id, slug=slug)

    else:
        review_form = ReviewForm()

    return render(request, 'blog/post_detail.html', {
        'product': product,
        'cart_product_form': cart_product_form,
        'review_form': review_form,
        'reviews': reviews,  # Paginated reviews
    })





from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import requests

from django.shortcuts import redirect


import requests
from django.http import JsonResponse
from django.urls import reverse
import requests
from django.contrib.auth.decorators import login_required

@login_required  # Декоратор, чтобы проверить, что пользователь аутентифицирован
def like_material(request, material_id):
    material = get_object_or_404(BuildingMaterials, pk=material_id)

    try:
        user_profile = request.user.profile
    except AttributeError:
        user_profile = None

    # Создаем объект Like, связывая его с профилем пользователя и материалом
    like, created = Like.objects.get_or_create(user=user_profile, material=material)

    # Перенаправляем пользователя обратно на страницу материала
    return HttpResponseRedirect(reverse('main:post-detail', args=[material_id, material.slug]))

from rest_framework.decorators import api_view

from .tasks import email_send_message
def import_contacts_and_send_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if email:
            email_send_message.delay(email)
            return redirect('main:index')
        else:
            return JsonResponse({"error": "Email не указан."}, status=400)
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
    paginate_by = 4

    def get_queryset(self):
        # Получаем queryset всех объектов BuildingMaterials
        queryset = super().get_queryset()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_objects = context['post']
        paginator = Paginator(page_objects, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_objects = paginator.get_page(page_number)

        if self.request.user.is_authenticated:
            user_profile = self.request.user.profile  # Предположим, что у пользователя есть профиль
            for material in page_objects:
                material.is_liked = Like.objects.filter(user=user_profile, material=material).exists()

        context['post'] = page_objects
        random_objects = list(BuildingMaterials.objects.order_by('?')[:self.paginate_by])
        context['post'] = random_objects

        populars = BuildingMaterials.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:self.paginate_by]
        context['populars'] = populars

        return context


from django.shortcuts import render, redirect
from .forms import RegistrationForm, ReviewForm


# Create your views here.



class RegistrationView(View):
    form_class = RegistrationForm
    template_name = 'blog/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(username=username, email=email, password=password, role=True)
            profile = Profile.objects.create(user=user, email=email)

            if profile:
                print(f'Profile created successfully for {username}')

            return redirect('main:login')
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
            if user.role == True:
                login(request, user)
                return redirect('main:index')  # Перенаправление на нужную страницу для роли False
            else:
                # Роль True - перенаправляем на другую страницу
                return redirect('provider:login')  # Замените 'main:some_other_page' на нужный URL
        else:
            # Пользователь с указанными учетными данными не найден, перезагрузка страницы
            return redirect('provider:login')  # Перенаправление на ту же страницу в случае ошибки ввода
    else:
        return render(request, 'blog/login.html')

class ViewCatalog(ListView):
    model = BuildingMaterials
    template_name = 'blog/catalog.html'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()

        if 'liked_posts' in self.request.GET and self.request.user.is_authenticated:
            liked_posts = self.request.GET['liked_posts']
            if liked_posts == 'on':
                user = self.request.user
                queryset = queryset.filter(likes__user=user)

        return queryset.annotate(like_count=Count('likes'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        # Получаем материалы с учетом фильтрации
        materials = self.get_queryset()

        # Пагинация
        page_number = self.request.GET.get('page')
        paginator = Paginator(materials, self.paginate_by)
        page_objects = paginator.get_page(page_number)

        if self.request.user.is_authenticated:
            user_profile = self.request.user.profile
            for material in page_objects:
                material.is_liked = Like.objects.filter(user=user_profile, material=material).exists()

        context['materials'] = page_objects
        context['is_paginated'] = True
        context['is_catalog_page'] = True
        return context

from django.db.models import Q
def search_results(request):
    query = request.GET.get('q')
    categories = Category.objects.all()
    materials = BuildingMaterials.objects.all()

    if query:
        title_filter = Q(title__icontains=query)
        materials = materials.filter(title_filter)

        if request.user.is_authenticated and 'liked_posts' in request.GET and request.GET['liked_posts'] == 'on':
            likes_filter = Q(likes__user=request.user)
            materials = materials.annotate(like_count=Count('likes'))
            materials = materials.filter(title_filter & likes_filter)


    paginator = Paginator(materials, 9)
    page_number = request.GET.get('page')

    try:
        materials_paginated = paginator.page(page_number)
        is_paginated = True
    except PageNotAnInteger:
        materials_paginated = paginator.page(1)
        is_paginated = True
    except EmptyPage:
        materials_paginated = paginator.page(paginator.num_pages)
        is_paginated = True

    if request.user.is_authenticated:
        user_profile = request.user.profile
        for material in materials_paginated:
            material.is_liked = Like.objects.filter(user=user_profile, material=material).exists()

    return render(request, 'blog/catalog.html', {
        'categories': categories,
        'materials': materials_paginated,
        'query': query,
        'is_catalog_page': True,
        'is_paginated': is_paginated
    })

from django.db.models import Count


def filter_posts(request, url):
    materials = BuildingMaterials.objects.filter(category__url=url)
    categories = Category.objects.all()

    if 'liked_posts' in request.GET and request.GET['liked_posts'] == 'on' and request.user.is_authenticated:
        materials = materials.filter(likes__user=request.user.id)

    materials = materials.annotate(like_count=Count('likes'))

    paginator = Paginator(materials, 9)
    page_number = request.GET.get('page')

    try:
        materials_paginated = paginator.page(page_number)
        is_paginated = True
    except PageNotAnInteger:
        materials_paginated = paginator.page(1)
        is_paginated = True
    except EmptyPage:
        materials_paginated = paginator.page(paginator.num_pages)
        is_paginated = True

    if request.user.is_authenticated:
        user_profile = request.user.profile
        for material in materials_paginated:
            material.is_liked = Like.objects.filter(user=user_profile, material=material).exists()

    return render(request, 'blog/catalog.html', {
        'categories': categories,
        'materials': materials_paginated,
        'is_paginated': is_paginated,
        'is_catalog_page': True
    })
class ProfileForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['image', 'first_name', 'last_name', 'postal_code', 'city', 'email', 'address']
class ProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'blog/Profile.html'
    context_object_name = 'profile'
    form_class = ProfileForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse('main:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Order = OrderItem.objects.filter(profile=self.request.user.profile).count()
        context['order'] = Order
        return context