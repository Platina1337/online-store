from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.models import User
from django.core.checks import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView
from django.views.generic import ListView
from .forms import RegistrationProviderForm, AddPostForm
from main.models import Profile, BuildingMaterials, Category, Review


class RegistrationProviderView(View):
    form_class = RegistrationProviderForm
    template_name = 'provider/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            city = form.cleaned_data['city']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            passport_number = form.cleaned_data['passport_number']
            passport_series = form.cleaned_data['passport_series']

            # Отладочные сообщения
            print(f'Username: {username}')
            print(f'Email: {email}')
            print(f'Password: {password}')
            print(f'City: {city}')
            print(f'First Name: {first_name}')
            print(f'Last Name: {last_name}')
            print(f'Passport Number: {passport_number}')
            print(f'Passport Series: {passport_series}')
            User = get_user_model()
            user = User.objects.create_user(username=username, email=email, password=password, role=False)
            profile = Profile.objects.create(
                user=user,
                email=email,
                passport_series=passport_series,
                passport_number=passport_number,
                last_name=last_name,
                first_name=first_name,
                city=city
            )

            # Отладочные логи
            print(f'User: {user}')
            print(f'Profile: {profile}')

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
            if user.role == False:
                login(request, user)
                return redirect('provider:add')  # Перенаправление на нужную страницу для роли False
            else:
                # Роль True - перенаправляем на другую страницу
                return redirect('main:login')  # Замените 'main:some_other_page' на нужный URL
        else:
            # Пользователь с указанными учетными данными не найден, перезагрузка страницы
            return redirect('main:login')  # Перенаправление на ту же страницу в случае ошибки ввода
    else:
        return render(request, 'blog/login.html')

class BuildingMaterialsCreateView(CreateView):
    model = BuildingMaterials
    form_class = AddPostForm
    success_url = '/provider/list_posts/'
    template_name = 'provider/add.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        return context

    def form_valid(self, form):
        building_material = form.save(commit=False)
        building_material.author = self.request.user.profile
        building_material.category = form.cleaned_data['category']
        building_material.slug = slugify(f"{building_material.title}-{building_material.author.id}-{building_material.category.id}")
        building_material.save()
        return super().form_valid(form)

class PostDetailView(DetailView):
    model = BuildingMaterials
    template_name = 'provider/post_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        material_id = self.kwargs.get('pk')
        # Получаем BuildingMaterials по ID и проверяем, что он принадлежит текущему пользователю
        return get_object_or_404(BuildingMaterials, id=material_id, author=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        if product:
            reviews = Review.objects.filter(post=product)
            paginator = Paginator(reviews, 4)
            page_number = self.request.GET.get('page')  # Получаем текущий номер страницы
            try:
                reviews = paginator.page(page_number)
            except PageNotAnInteger:
                reviews = paginator.page(1)  # Если номер страницы не является целым числом, возвращаем первую страницу
            except EmptyPage:
                reviews = paginator.page(paginator.num_pages)  # Если страница пуста, возвращаем последнюю страницу

            context['reviews'] = reviews
        return context


class ListPosts(ListView):
    model = BuildingMaterials
    template_name = 'provider/posts.html'
    context_object_name = 'materials'

    def get_queryset(self):
        # Возвращаем QuerySet объектов BuildingMaterials,
        # фильтрованных по пользователю, для отображения в ListView
        return BuildingMaterials.objects.filter(author=self.request.user.profile)
def delete_material(request):
    if request.method == 'POST':
        material_id = request.POST.get('material_id')
        material = get_object_or_404(BuildingMaterials, id=material_id)
        material.delete()

        return redirect(reverse('provider:list_posts'))  # Replace 'materials_list' with your actual view name
    return redirect(reverse('provider:list_posts'))