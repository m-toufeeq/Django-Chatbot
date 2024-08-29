

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
def start_chat(request):
    # Get the first flow for the user (this can be customized)
    user_profile = UserProfile.objects.get(user=request.user)
    flow = Flow.objects.first()  # Choose the flow you want to start
    first_step = FlowStep.objects.filter(flow=flow).order_by('step_number').first()

    # Start the chat by returning the first step
    return JsonResponse({
        'step_id': first_step.id,
        'text': first_step.text,
        'options': list(first_step.options.values('id', 'text'))
    })

# Handle User Response View
@login_required
def handle_response(request, step_id, option_id):
    step = FlowStep.objects.get(id=step_id)
    option = FlowOption.objects.get(id=option_id)

    # Save the user's response
    UserResponse.objects.create(
        user=UserProfile.objects.get(user=request.user),
        step=step,
        response=option.text
    )

    # Determine the next step
    if option.next_step:
        next_step = option.next_step
        response_data = {
            'step_id': next_step.id,
            'text': next_step.text,
            'options': list(next_step.options.values('id', 'text'))
        }
    else:
        # End of flow
        response_data = {
            'text': "Thank you for completing the flow!",
            'options': []
        }

    return JsonResponse(response_data)


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
