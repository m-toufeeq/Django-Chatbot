from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .forms import SignUpForm
from .models import *
from django.views.decorators.http import require_POST
import json

def flow_buttons(request):
    flows = Flow.objects.all()
    buttons = [{'id': flow.id, 'text': flow.name} for flow in flows]  
    return JsonResponse(buttons, safe=False)
    
@login_required
@require_POST
def start_chat(request):
    # Parse the received JSON data from the POST request
    data = json.loads(request.body)
    flow_text = data.get('flow_text')

    # Retrieve the Flow object based on the button text
    try:
        flow = Flow.objects.get(name=flow_text)  # Assuming Flow model has a 'name' field
    except Flow.DoesNotExist:
        return JsonResponse({'error': 'Flow not found'}, status=404)

    # Get the first step of the chosen flow
    first_step = FlowStep.objects.filter(flow=flow).order_by('step_number').first()

    if not first_step:
        return JsonResponse({'error': 'No steps found for this flow'}, status=404)

    # Return the first step of the flow along with the available options
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
    flow = Flow.objects.all()
    return redirect('dashboard')

    
@login_required
def flowcreate(request):
    if request.method == 'POST':
        pass  

    # Fetch existing flows if needed
    flows = Flow.objects.all()

    return render(request, 'ChabotFeature/flow_create.html', {'flows': flows})

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
