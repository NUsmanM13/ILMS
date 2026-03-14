import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Subject, Question, ExamSession
from django.db import models  # Mana shu qatorni qo'shing

@login_required
def exam_home(request):
    subjects = Subject.objects.prefetch_related('questions').all()
    # Foydalanuvchining oxirgi 5 ta imtihon natijasi
    user_results = ExamSession.objects.filter(user=request.user, is_finished=True).order_by('-started_at')[:5]
    
    # Umumiy statistika
    total_exams = ExamSession.objects.filter(user=request.user, is_finished=True).count()
    avg_score = ExamSession.objects.filter(user=request.user, is_finished=True).aggregate(models.Avg('score'))['score__avg'] or 0

    return render(request, 'quiz/home.html', {
        'subjects': subjects,
        'user_results': user_results,
        'total_exams': total_exams,
        'avg_score': round(avg_score, 1)
    })

@login_required
def start_exam(request, subject_id, exam_type):
    subject = get_object_or_404(Subject, id=subject_id)
    session = ExamSession.objects.create(
        user=request.user,
        subject=subject,
        exam_type=exam_type
    )
    
    # Savollarni tayyorlash (Oddiy va Koeffitsiyentli uchun oldindan tanlanadi)
    if exam_type in ['simple', 'coefficient']:
        questions = list(Question.objects.filter(subject=subject).values_list('id', flat=True))
        random.shuffle(questions)
        request.session[f'questions_{session.id}'] = questions[:25] # 25 ta savol
    else:
        # Adaptive uchun savollar dinamik tanlanadi, hozircha bo'sh
        request.session[f'questions_{session.id}'] = []
        request.session[f'current_level_{session.id}'] = 3 # 3-darajadan boshlanadi
        request.session[f'adaptive_history_{session.id}'] = [] # To'plangan baholar

    request.session[f'current_index_{session.id}'] = 0
    request.session[f'score_{session.id}'] = 0.0
    request.session[f'correct_count_{session.id}'] = 0
    
    return redirect('quiz:take_test', session_id=session.id)

@login_required
def take_test(request, session_id):
    session = get_object_or_404(ExamSession, id=session_id, user=request.user)
    q_list = request.session.get(f'questions_{session.id}', [])
    idx = request.session.get(f'current_index_{session.id}', 0)
    
    # Imtihon yakuni tekshiruvi (masalan 25 ta savoldan keyin)
    if idx >= 25:
        return finish_exam(request, session)

    # Savolni aniqlash
    if session.exam_type == 'adaptive':
        level = request.session.get(f'current_level_{session.id}', 3)
        question = Question.objects.filter(subject=session.subject, level=level).exclude(id__in=q_list).order_by('?').first()
        if not question: # Agar bu darajada savol qolmasa, eng yaqin darajani olamiz
            question = Question.objects.filter(subject=session.subject).exclude(id__in=q_list).order_by('?').first()
    else:
        question = Question.objects.get(id=q_list[idx])

    if request.method == "POST":
        selected = int(request.POST.get('option', 0))
        is_correct = (selected == question.correct_option)
        
        # Mantiqiy hisob-kitoblar
        if is_correct:
            request.session[f'correct_count_{session.id}'] += 1
            if session.exam_type == 'simple':
                request.session[f'score_{session.id}'] += 4 # 25 * 4 = 100
            elif session.exam_type == 'coefficient':
                request.session[f'score_{session.id}'] += question.coefficient
            elif session.exam_type == 'adaptive':
                request.session[f'adaptive_history_{session.id}'].append(question.level)
                # Darajani oshirish
                if question.level < 5:
                    request.session[f'current_level_{session.id}'] = question.level + 1
        else:
            if session.exam_type == 'adaptive':
                # Darajani tushirish
                if question.level > 3:
                    request.session[f'current_level_{session.id}'] = question.level - 1

        request.session[f'questions_{session.id}'].append(question.id)
        request.session[f'current_index_{session.id}'] += 1
        return redirect('quiz:take_test', session_id=session.id)

    return render(request, 'quiz/take_test.html', {
        'question': question,
        'index': idx + 1,
        'session': session
    })

def finish_exam(request, session):
    session.is_finished = True
    session.total_questions = request.session[f'current_index_{session.id}']
    session.correct_answers = request.session[f'correct_count_{session.id}']
    
    if session.exam_type == 'adaptive':
        history = request.session.get(f'adaptive_history_{session.id}', [])
        if history:
            # Eng ko'p to'g'ri javob berilgan darajani topish (Baho sifatida)
            most_frequent_level = max(set(history), key=history.count())
            # 60% dan o'tsa o'sha daraja, bo'lmasa 2 (yiqildi)
            percent = (len(history) / session.total_questions) * 100
            session.final_grade = most_frequent_level if percent >= 60 else 2
            session.score = percent
    else:
        session.score = request.session[f'score_{session.id}']

    session.save()
    return render(request, 'quiz/result.html', {'session': session})