from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Module, Topic, Element, Question, UserProgress

@login_required
def course_list(request):
    """Barcha kurslar va ulardagi progressni ko'rsatish"""
    courses = Course.objects.all()
    courses_data = []

    for course in courses:
        # Kursdagi jami mavzular soni
        all_topics = Topic.objects.filter(module__course=course)
        total_topics_count = all_topics.count()
        
        # Tugatilgan mavzular soni
        passed_topics_count = UserProgress.objects.filter(
            user=request.user, 
            topic__module__course=course, 
            is_passed=True
        ).count()
        
        # Progress foizi
        percent = int((passed_topics_count / total_topics_count) * 100) if total_topics_count > 0 else 0
        
        # Birinchi darsga kirish nuqtasi (3-darajali element)
        first_topic = all_topics.order_by('module__order', 'order').first()
        first_element_id = None
        if first_topic:
            first_el = Element.objects.filter(topic=first_topic, difficulty=3).first()
            if first_el:
                first_element_id = first_el.id

        courses_data.append({
            'course': course,
            'percent': percent,
            'first_element_id': first_element_id
        })

    return render(request, 'adaptive/course_list.html', {'courses_data': courses_data})


@login_required
def element_detail(request, element_id):
    """Dars detallari, Test topshirish va Adaptiv mantiq"""
    # select_related ishlatish DB so'rovlarini kamaytiradi
    element = get_object_or_404(Element.objects.select_related('topic__module__course'), id=element_id)
    topic = element.topic
    course = topic.module.course
    user = request.user
    
    # --- 1. ACCESS CONTROL (LOCKING SYSTEM) ---
    all_course_topics = Topic.objects.filter(
        module__course=course
    ).order_by('module__order', 'order')
    
    previous_topic = None
    for t in all_course_topics:
        if t == topic:
            break
        previous_topic = t
        
    if previous_topic:
        prev_progress = UserProgress.objects.filter(user=user, topic=previous_topic, is_passed=True).exists()
        if not prev_progress:
            messages.warning(request, "Avvalgi mavzuni yakunlamasdan turib keyingi mavzuga o'ta olmaysiz.")
            return redirect('adaptive:course_list')

    # --- 2. TEST TOPSHIRISH (POST METHOD) ---
    questions = element.questions.all()
    modal_data = None

    if request.method == "POST":
        correct_count = 0
        total_q = questions.count()
        for q in questions:
            ans = request.POST.get(f'q_{q.id}')
            if ans and int(ans) == q.correct_option:
                correct_count += 1
        
        score_percent = int((correct_count / total_q) * 100) if total_q > 0 else 0
        is_passed = score_percent >= 60

        # Progressni DB da yangilash yoki yaratish
        progress, created = UserProgress.objects.get_or_create(
            user=user, topic=topic,
            defaults={
                'element': element, 
                'score': score_percent, 
                'is_passed': is_passed, 
                'highest_level': element.difficulty
            }
        )
        
        if not created:
            if is_passed:
                progress.is_passed = True
                # Yaxshiroq natija bo'lsagina yangilaymiz
                if score_percent > progress.score:
                    progress.score = score_percent
                if element.difficulty > progress.highest_level:
                    progress.highest_level = element.difficulty
                progress.element = element
            progress.save()

        # --- 3. ADAPTIVE LOGIC (KEYINGI QADAMNI ANIQLASH) ---
        if is_passed:
            higher_levels = Element.objects.filter(topic=topic, difficulty__gt=element.difficulty).order_by('difficulty')
            
            next_topic = None
            found_current = False
            for t in all_course_topics:
                if found_current:
                    next_topic = t
                    break
                if t == topic:
                    found_current = True
            
            next_topic_elements = Element.objects.filter(topic=next_topic).order_by('difficulty') if next_topic else []
            
            modal_data = {
                'status': 'success',
                'score': score_percent,
                'higher_levels': higher_levels,
                'next_topic': next_topic,
                'next_topic_elements': next_topic_elements,
                'current_difficulty': element.difficulty
            }
        else:
            lower_levels = Element.objects.filter(topic=topic, difficulty__lt=element.difficulty).order_by('-difficulty')
            modal_data = {
                'status': 'fail',
                'score': score_percent,
                'lower_levels': lower_levels,
                'current_difficulty': element.difficulty
            }

    # --- 4. SIDEBAR VA PROGRESS (SHABLONGA MOSLAB) ---
    passed_topics_ids = UserProgress.objects.filter(user=user, is_passed=True).values_list('topic_id', flat=True)
    
    total_topics_count = all_course_topics.count()
    passed_count = len(passed_topics_ids)
    progress_percent = int((passed_count / total_topics_count) * 100) if total_topics_count > 0 else 0

    sidebar_items = []
    unlocked = True 
    for t in all_course_topics:
        is_comp = t.id in passed_topics_ids
        first_el = t.elements.order_by('difficulty').first()
        
        sidebar_items.append({
            'topic': t,
            'is_active': t.id == topic.id,
            'is_locked': not unlocked,
            'is_completed': is_comp,
            'url': first_el.id if first_el else None
        })
        unlocked = is_comp

    # Video URL ni embed formatga o'tkazish
    video_embed = None
    if element.video_url:
        url = element.video_url
        if "watch?v=" in url:
            video_embed = url.replace("watch?v=", "embed/")
        elif "youtu.be/" in url:
            video_embed = url.replace("youtu.be/", "youtube.com/embed/")
        elif "vimeo.com/" in url:
            video_embed = url.replace("vimeo.com/", "player.vimeo.com/video/")

    context = {
        'element': element,
        'topic': topic,
        'questions': questions,
        'modal_data': modal_data,
        'sidebar_items': sidebar_items,
        'progress_percent': progress_percent,
        'video_embed': video_embed,
    }

    return render(request, 'adaptive/element_detail.html', context)