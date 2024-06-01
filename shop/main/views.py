from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
import redis
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from typing import Any
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, UpdateView
from .models import BuildingMaterials, Review, Like, Profile, Category, User, Contact
from django.views.decorators.http import require_POST
from cart.forms import CartAddProductForm
from news.models import Video
from orders.models import OrderItem

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


def product_detail(request, id, slug):
    product = get_object_or_404(BuildingMaterials, id=id, slug=slug, available=True)
    reviews = Review.objects.filter(post=product)
    current_user = request.user

    # Инкремент количества просмотров в Redis
    redis_key = f'image:{product.id}:views'
    total_views = r.incr(redis_key)

    # Обновление количества просмотров в базе данных
    product.views = total_views
    product.save(update_fields=['views'])

    total_likes = product.likes.count()
    is_liked = product.likes.filter(id=request.user.id).exists()

    # Пагинация - Показывать 4 отзыва на страницу
    paginator = Paginator(reviews, 4)
    page_number = request.GET.get('page')
    try:
        reviews = paginator.page(page_number)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

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
        'reviews': reviews,
        'current_user': current_user,
        'total_views': total_views,
        'total_likes': total_likes,
        'is_liked': is_liked,
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



from .tasks import email_send_message, logger

def import_contacts_and_send_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if email:
            logger.info(f'Received email: {email}')
            email_send_message.delay(email)
            logger.info('Task has been sent to Celery')
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
            user_profile = self.request.user.profile
            for material in page_objects:
                material.is_liked = Like.objects.filter(user=user_profile, material=material).exists()

        context['post'] = page_objects
        random_objects = list(BuildingMaterials.objects.order_by('?')[:self.paginate_by])
        if self.request.user.is_authenticated:
            for material in random_objects:
                material.is_liked = Like.objects.filter(user=self.request.user.profile, material=material).exists()
        context['random_objects'] = random_objects

        populars = BuildingMaterials.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:self.paginate_by]
        if self.request.user.is_authenticated:
            for material in populars:
                material.is_liked = Like.objects.filter(user=self.request.user.profile, material=material).exists()
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

            User = get_user_model()
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

@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user_to = Profile.objects.get(user__id=user_id)
            user_from = request.user.profile
            if action == 'follow':
                Contact.objects.get_or_create(user_from=user_from, user_to=user_to)
            else:
                Contact.objects.filter(user_from=user_from, user_to=user_to).delete()
            return JsonResponse({'status': 'ok'})
        except Profile.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})

class FollowingListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'blog/following_list.html'
    context_object_name = 'following_list'

    def get_queryset(self):
        return self.request.user.profile.following.all()

