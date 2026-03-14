from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Assignment, Submission
from .forms import SubmissionForm
from django.contrib import messages

@login_required
def assignment_list(request):
    assignments = Assignment.objects.all().order_by('-created_at')
    # Talaba qaysi topshiriqlarni topshirib bo'lganini bilish uchun
    user_submissions = Submission.objects.filter(user=request.user).values_list('assignment_id', flat=True)
    return render(request, 'practical/list.html', {
        'assignments': assignments,
        'user_submissions': user_submissions
    })

@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    submission = Submission.objects.filter(assignment=assignment, user=request.user).first()
    
    if request.method == 'POST':
        if submission:
            messages.warning(request, "Siz allaqachon javob yuborgansiz!")
            return redirect('practical:detail', pk=pk)
            
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            new_sub = form.save(commit=False)
            new_sub.user = request.user
            new_sub.assignment = assignment
            new_sub.save()
            messages.success(request, "Javobingiz muvaffaqiyatli qabul qilindi!")
            return redirect('practical:detail', pk=pk)
    else:
        form = SubmissionForm()

    return render(request, 'practical/detail.html', {
        'assignment': assignment,
        'submission': submission,
        'form': form
    })