

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .forms import SignUpForm
from .models import *
# @login_required
# def index(request):
#     # Retrieve visit count from session or initialize it to 0
#     visit_count = request.session.get('visit_count', 0)
    
#     # Increment the count
#     visit_count += 1
    
#     # Store the updated count back in the session
#     request.session['visit_count'] = visit_count
    
#     # Pass the visit count to the template
#     return render(request, 'ChabotFeature/index.html', {'visit_count': visit_count})

@login_required
def index(request):
    # Redirect to the dashboard view
    return redirect('dashboard')

@login_required
def dashboard_view(request):
    return render(request, 'ChabotFeature/index.html')

def signup_view(request):
    if request.method == 'POST':
        print(request.POST)
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # user = authenticate(username=user.username, password=form.cleaned_data.get('password1'))
            
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        form = SignUpForm()
    return render(request, 'ChabotFeature/register.html', {'form': form})
