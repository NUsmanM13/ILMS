from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Lesson, Module, Element, UserProgress, Question

@login_required
def lesson_list(request):
    lessons_data = []
    lessons = Lesson.objects.prefetch_related('modules__elements').all()
    
    for lesson in lessons:
        percent = lesson.get_progress_percent(request.user)
        lessons_data.append({
            'lesson': lesson,
            'percent': int(percent) if percent else 0
        })
    
    return render(request, 'elementar/lesson_list.html', {'lessons_data': lessons_data})
# elementar/views.py



@login_required
def element_detail(request, element_id):
    lessons = Lesson.objects.all()
    element = get_object_or_404(Element, id=element_id)
    lesson = element.module.lesson
    modules = lesson.modules.prefetch_related('elements').all()
    current_lesson_percent = lesson.get_progress_percent(request.user)

    # Keyingi elementni topish (Logika: joriy modulda keyingisi, bo'lmasa keyingi modulning birinchisi)
    next_element = Element.objects.filter(module=element.module, order__gt=element.order).first()
    if not next_element:
        next_module = Module.objects.filter(lesson=lesson, order__gt=element.module.order).first()
        if next_module:
            next_element = next_module.elements.order_by('order').first()

    # Navbar uchun barcha darslar
    lessons_data = Lesson.objects.prefetch_related('modules__elements').all()
    # YouTube URLni embed formatga o'tkazish
    embed_url = ""
    if element.video_url:
        if "watch?v=" in element.video_url:
            embed_url = element.video_url.replace("watch?v=", "embed/")
        elif "youtu.be/" in element.video_url:
            embed_url = element.video_url.replace("youtu.be/", "youtube.com/embed/")
        else:
            embed_url = element.video_url

    completed_elements = UserProgress.objects.filter(
        user=request.user, is_completed=True
    ).values_list('element_id', flat=True)

    test_passed = element.id in completed_elements
    error = None

    if request.method == "POST" and not test_passed:
        selected_option = request.POST.get('option')
        if selected_option and int(selected_option) == element.quiz.correct_option:
            UserProgress.objects.get_or_create(user=request.user, element=element, is_completed=True)
            return redirect('elementar:element_detail', element_id=element.id)
        else:
            error = "Xato javob! Iltimos, materialni qayta o'qing."

    return render(request, 'elementar/element_detail.html', {
        'lessons_data': lessons_data,
        'current_lesson_percent': current_lesson_percent,
        'next_element': next_element,
        'element': element,
        'modules': modules,
        'completed_elements': completed_elements,
        'test_passed': test_passed,
        'error': error,
        'embed_url': embed_url, # Yangi o'zgaruvchi
    })
    element = get_object_or_404(Element, id=element_id)
    lesson = element.module.lesson
    modules = lesson.modules.prefetch_related('elements').all()
    
    # Foydalanuvchi bajargan elementlar ro'yxati
    completed_elements = UserProgress.objects.filter(
        user=request.user, is_completed=True
    ).values_list('element_id', flat=True)

    test_passed = element.id in completed_elements
    error = None

    if request.method == "POST" and not test_passed:
        selected_option = request.POST.get('option')
        if selected_option and int(selected_option) == element.quiz.correct_option:
            UserProgress.objects.get_or_create(user=request.user, element=element, is_completed=True)
            return redirect('elementar:element_detail', element_id=element.id)
        else:
            error = "Xato javob! Iltimos, materialni qayta o'qing."

    # views.py ichida element_detail funksiyasiga qo'shing:
    next_element = Element.objects.filter(
        module__lesson=lesson, 
        order__gt=element.order,
        module__order__gte=element.module.order
    ).exclude(id=element.id).order_by('module__order', 'order').first()

    # Agar joriy modul tugagan bo'lsa, keyingi modulning birinchi elementini topish:
    if not next_element:
        next_module = Module.objects.filter(lesson=lesson, order__gt=element.module.order).first()
        if next_module:
            next_element = next_module.elements.first()

    # Context-ga 'next_element': next_element deb uzating.


    return render(request, 'elementar/element_detail.html', {
        'lessons': lessons,
        'element': element,
        'modules': modules,
        'completed_elements': completed_elements,
        'test_passed': test_passed,
        'error': error
    })