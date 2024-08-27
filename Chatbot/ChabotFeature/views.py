from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm

@login_required
def index(request):
    # Retrieve visit count from session or initialize it to 0
    visit_count = request.session.get('visit_count', 0)
    
    # Increment the count
    visit_count += 1
    
    # Store the updated count back in the session
    request.session['visit_count'] = visit_count
    
    # Pass the visit count to the template
    return render(request, 'ChabotFeature/index.html', {'visit_count': visit_count})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            
            # Initialize session data upon registration
            request.session['visit_count'] = 0  # Initialize visit count for the user
            request.session.set_expiry(0)  # Optional: session expires when browser closes
            
            return redirect('index')  # Redirect to the homepage
    else:
        form = RegisterForm()

    return render(request, 'ChabotFeature/register.html', {'form': form})

def homepage(request):
    return render(request, 'ChabotFeature/homepage.html', )