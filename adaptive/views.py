from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Module, Element, Progress, Question
from django.db.models import Max


@login_required
def course_list(request):
    courses = Course.objects.prefetch_related('modules__elements').all()
    courses_with_progress = []

    for course in courses:
        # Umumiy elementlar soni
        total_elements = Element.objects.filter(module__course=course).count()
        # Tugatilgan elementlar soni
        completed_count = Progress.objects.filter(
            user=request.user, 
            element__module__course=course, 
            completed=True
        ).count()
        
        # Foiz hisoblash
        percent = int((completed_count / total_elements) * 100) if total_elements > 0 else 0
        
        # Birinchi dars id si (Kursni boshlash tugmasi uchun)
        first_element = Element.objects.filter(module__course=course).order_by('order').first()

        courses_with_progress.append({
            'course': course,
            'percent': percent,
            'first_element_id': first_element.id if first_element else None
        })

    return render(request, 'adaptive/course_list.html', {'courses_data': courses_with_progress})

@login_required
def element_detail(request, element_id):
    # 1. Joriy elementni olish
    element = get_object_or_404(Element, id=element_id)
    course = element.module.course
    user = request.user

    # 2. Kursdagi barcha elementlarni tartib bilan olish
    all_elements = Element.objects.filter(module__course=course).order_by('order')
    
    # 3. Foydalanuvchi tugatgan darslarni olish
    completed_elements = Progress.objects.filter(user=user, element__module__course=course, completed=True).values_list('element_id', flat=True)

    # 4. ADAPTIVE LOGIKA: Ruxsatni tekshirish
    # Foydalanuvchiga ruxsat berilgan darslar: (Tugatganlari + keyingi 1 ta dars)
    last_completed_order = Element.objects.filter(id__in=completed_elements).aggregate(Max('order'))['order__max'] or 0
    
    # Agar foydalanuvchi ruxsat etilmagan (qulflangan) darsga kirmoqchi bo'lsa:
    if element.order > last_completed_order + 1:
        # Uni ruxsat etilgan eng oxirgi darsga yo'naltiramiz
        first_locked = all_elements.filter(order__gt=last_completed_order).first()
        return redirect('adaptive:element_detail', element_id=first_element.id if not first_locked else first_locked.id)

    # 5. Sidebar uchun ma'lumotlarni shakllantirish
    sidebar_data = []
    for el in all_elements:
        sidebar_data.append({
            'id': el.id,
            'title': el.title,
            'is_completed': el.id in completed_elements,
            'is_active': el.id == element.id,
            'is_locked': el.order > last_completed_order + 1
        })

    # 6. Test topshirish (POST)
    error = None
    if request.method == "POST":
        selected = request.POST.get('option')
        if selected and hasattr(element, 'quiz') and int(selected) == element.quiz.correct_option:
            Progress.objects.get_or_create(user=user, element=element, completed=True)
            return redirect('adaptive:element_detail', element_id=element.id)
        else:
            error = "Xato javob! Iltimos, ma'lumotni qayta ko'rib chiqing."

    # YouTube URL formatlash
    embed_url = element.video_url.replace("watch?v=", "embed/") if element.video_url else None

    return render(request, 'adaptive/element_detail.html', {
        'element': element,
        'sidebar_data': sidebar_data,
        'embed_url': embed_url,
        'test_passed': element.id in completed_elements,
        'error': error,
    })