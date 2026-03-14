from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
import json

# Bosh sahifa
def home(request):
    return render(request, 'core/home.html')

# Ro'yxatdan o'tish
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:home')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

# Tizimga kirish
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('core:home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

# Tizimdan chiqish
def logout_view(request):
    logout(request)
    return redirect('core:home')


import json
from django.http import JsonResponse
from .models import BotKnowledge

def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').lower()
            
            # Bazadagi barcha bilimlarni olamiz
            # (Agar baza juda katta bo'lsa, buni optimallashtirish mumkin)
            knowledges = BotKnowledge.objects.all()
            
            reply = None
            
            # Foydalanuvchi xabarida qatnashgan so'zlarga qarab bazadan qidiramiz
            for k in knowledges:
                # Agar bazadagi kalit so'z user xabarining ichida bo'lsa
                if k.keyword.lower() in user_message:
                    reply = k.answer
                    break # Birinchi topilgan moslikni olamiz
            
            # Agar mos keladigan hech narsa topilmasa
            if not reply:
                reply = "Kechirasiz, bu termin bo'yicha menda ma'lumot yo'q. Iltimos, boshqacharoq so'rab ko'ring yoki administratorga murojaat qiling."
                
            return JsonResponse({'reply': reply})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Faqat POST so\'rovlar qabul qilinadi'}, status=400)