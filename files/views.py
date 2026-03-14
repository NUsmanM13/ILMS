from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Folder, Material, Submission
from django.contrib import messages

@login_required
def folder_list(request):
    folders = Folder.objects.all().order_by('-created_at')
    return render(request, 'files/list.html', {'folders': folders})

@login_required
def folder_detail(request, pk):
    folder = get_object_or_404(Folder, pk=pk)
    materials = folder.materials.all() # Admin yuklaganlar
    
    # Talaba faqat o'z javobini ko'radi, Admin esa hammanikini
    if request.user.is_staff:
        submissions = folder.submissions.all()
    else:
        submissions = folder.submissions.filter(user=request.user)

    if request.method == 'POST':
        # Admin material yuklashi
        if 'add_material' in request.POST and request.user.is_staff:
            file = request.FILES.get('file')
            title = request.POST.get('title')
            is_task = 'is_assignment' in request.POST
            Material.objects.create(folder=folder, title=title, file=file, is_assignment=is_task)
            messages.success(request, "Material yuklandi!")
            
        # Talaba javob yuklashi
        elif 'submit_homework' in request.POST:
            file = request.FILES.get('homework_file')
            comment = request.POST.get('comment', '')
            Submission.objects.create(folder=folder, user=request.user, file=file, comment=comment)
            messages.success(request, "Vazifa topshirildi!")
            
        return redirect('files:detail', pk=folder.pk)

    return render(request, 'files/detail.html', {
        'folder': folder,
        'materials': materials,
        'submissions': submissions
    })