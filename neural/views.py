from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import AIPath, Module, Element, NeuralProgress

@login_required
def path_list(request):
    paths = AIPath.objects.all()
    data = []
    for p in paths:
        data.append({
            'path': p,
            'progress': p.get_essential_progress(request.user)
        })
    return render(request, 'neural/path_list.html', {'data': data})

@login_required
def element_detail(request, element_id):
    element = get_object_or_404(Element, id=element_id)
    path = element.module.path
    modules = path.modules.prefetch_related('elements').all()
    
    # Progress hisoblash
    progress_percent = path.get_essential_progress(request.user)
    completed_ids = NeuralProgress.objects.filter(user=request.user, completed=True).values_list('element_id', flat=True)

    if request.method == "POST":
        ans = request.POST.get('option')
        if ans and int(ans) == element.test.correct:
            NeuralProgress.objects.get_or_create(user=request.user, element=element, completed=True)
            return redirect('neural:element_detail', element_id=element.id)

    embed_url = element.video_url.replace("watch?v=", "embed/") if element.video_url else None

    return render(request, 'neural/element_detail.html', {
        'element': element,
        'modules': modules,
        'progress_percent': progress_percent,
        'completed_ids': completed_ids,
        'embed_url': embed_url,
        'is_completed': element.id in completed_ids,
    })