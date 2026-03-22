from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Lesson, Module, Element, UserProgress, Question

@login_required
def lesson_list(request):
    """Barcha darslar ro'yxati va ularning umumiy progressi"""
    lessons_data = []
    lessons = Lesson.objects.prefetch_related('modules__elements').all()
    
    for lesson in lessons:
        percent = lesson.get_progress_percent(request.user)
        lessons_data.append({
            'lesson': lesson,
            'percent': int(percent) if percent else 0
        })
    
    return render(request, 'elementar/lesson_list.html', {'lessons_data': lessons_data})


@login_required
def element_detail(request, element_id):
    """Dars detallari, nazariya va 60%lik chegara bilan test tekshirish"""
    element = get_object_or_404(Element.objects.select_related('module__lesson'), id=element_id)
    lesson = element.module.lesson
    user = request.user
    
    lessons_data = Lesson.objects.prefetch_related('modules__elements').all()
    modules = lesson.modules.prefetch_related('elements').all()
    questions = element.questions.all()
    
    # Keyingi elementni topish
    next_element = Element.objects.filter(module=element.module, order__gt=element.order).first()
    if not next_element:
        next_module = Module.objects.filter(lesson=lesson, order__gt=element.module.order).first()
        if next_module:
            next_element = next_module.elements.order_by('order').first()

    # Video URLni formatlash
    embed_url = ""
    if element.video_url:
        url = element.video_url
        if "watch?v=" in url:
            embed_url = url.replace("watch?v=", "embed/")
        elif "youtu.be/" in url:
            embed_url = url.replace("youtu.be/", "www.youtube.com/embed/")
        else:
            embed_url = url

    # Progress holatini tekshirish
    user_progress = UserProgress.objects.filter(user=user, element=element).first()
    is_completed = user_progress.is_completed if user_progress else False
    
    completed_elements_ids = UserProgress.objects.filter(
        user=user, is_completed=True
    ).values_list('element_id', flat=True)

    error = None
    success = False
    score_percent = 0

    # TEST TOPSHIRISH (POST METHOD)
    if request.method == "POST" and not is_completed:
        total_questions = questions.count()
        correct_count = 0
        
        for q in questions:
            selected_option = request.POST.get(f'q_{q.id}')
            if selected_option and int(selected_option) == q.correct_option:
                correct_count += 1
        
        # Natijani foizda hisoblash
        if total_questions > 0:
            score_percent = int((correct_count / total_questions) * 100)
        else:
            score_percent = 100 # Agar savollar bo'lmasa

        # 60% lik o'tish chegarasi
        if score_percent >= 60:
            # Natijani bazaga yozamiz
            progress, created = UserProgress.objects.update_or_create(
                user=user, element=element,
                defaults={'is_completed': True, 'score': score_percent}
            )
            success = True
            is_completed = True
        else:
            error = f"Natija: {score_percent}%. O'tish uchun kamida 60% kerak. Siz {total_questions} tadan {correct_count} tasini topdingiz."

    current_lesson_percent = lesson.get_progress_percent(user)

    return render(request, 'elementar/element_detail.html', {
        'lessons_data': lessons_data,
        'current_lesson_percent': current_lesson_percent,
        'next_element': next_element,
        'element': element,
        'questions': questions,
        'modules': modules,
        'completed_elements': completed_elements_ids,
        'test_passed': is_completed,
        'user_score': user_progress.score if user_progress else score_percent,
        'error': error,
        'success': success,
        'embed_url': embed_url,
    })