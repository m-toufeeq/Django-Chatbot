from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required



@login_required
def index(request):
    return render(request, 'ChabotFeature/index.html')
    

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user
            return redirect('index')  # Redirect to the homepage after registration
    else:
        form = RegisterForm()

    return render(request, 'ChabotFeature/register.html', {'form': form})
