from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
from main.models import BuildingMaterials, Profile
from .models import Dialog, Message
from .forms import MessageForm
from django.views.generic import ListView


# Create your views here.
@require_POST
@login_required
def create_dialog(request, id):
    product = get_object_or_404(BuildingMaterials, id=id)
    if product:
        member_to = request.user.profile
        member_from = product.author
        try:
            # Проверяем, существует ли диалог между участниками
            exist_dialog = Dialog.objects.filter(
                (Q(member_to=member_to) & Q(member_from=member_from)) |
                (Q(member_to=member_from) & Q(member_from=member_to))
            ).first()

            if not exist_dialog:
                # Создаем новый диалог
                exist_dialog = Dialog.objects.create(member_to=member_to, member_from=member_from)

            # Перенаправляем на страницу существующего или нового диалога
            return redirect(reverse('message:dialogs_view', kwargs={'member_from': exist_dialog.member_from.id}))
        except Profile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Profile does not exist'})

    return JsonResponse({'status': 'error', 'message': 'Product does not exist'})


@method_decorator(login_required, name='dispatch')
class DialogsView(View):
    def get(self, request, member_from):
        member_to = request.user.profile
        member_from_profile = get_object_or_404(Profile, id=member_from)

        chat = Dialog.objects.filter(
            (Q(member_to=member_to) & Q(member_from=member_from_profile)) |
            (Q(member_to=member_from_profile) & Q(member_from=member_to))
        ).first()

        form = MessageForm()
        context = {
            'user_profile': request.user.profile,
            'chat': chat,
            'form': form
        }
        return render(request, 'message/dialog.html', context)

    def post(self, request, member_from):
        member_to = request.user.profile
        member_from_profile = get_object_or_404(Profile, id=member_from)

        # Retrieve or create the dialog
        chat, created = Dialog.objects.get_or_create(
            member_to=member_to,
            member_from=member_from_profile,
            defaults={'member_to': member_to, 'member_from': member_from_profile}
        )

        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.author = request.user.profile
            message.save()
            return redirect('message:dialogs_view', member_from=member_from)

        context = {
            'user_profile': request.user.profile,
            'chat': chat,
            'form': form
        }
        return render(request, 'message/dialog.html', context)
class ListChatsView(View):
    def get(self, request):
        user_profile = request.user.profile
        chats = Dialog.objects.filter(member_to=user_profile) | Dialog.objects.filter(member_from=user_profile)
        return render(request, 'message/list_chats.html', {'user_profile': user_profile, 'chats': chats})