from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import SignUpForm
from .models import *
from django.views.decorators.http import require_POST
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.staticfiles import finders
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.middleware.csrf import get_token
import pandas as pd

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
    flow_text = flow_text.split("_")[0]
    #2_flow
    # Retrieve the Flow object based on the button text
    try:
        flow = Flow.objects.get(id=flow_text)
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
def flowview(request):
    if request.method == 'POST':
        # Handle form submission or other POST request processing here
        pass
    
    # Retrieve the UserProfile for the logged-in user
    try:
        userprofile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Handle the case where UserProfile does not exist
        # For example, redirect to an error page or create a UserProfile
        return render(request, 'ChabotFeature/error.html', {'message': 'UserProfile not found'})

    # Attempt to retrieve SymptomLog for the UserProfile
    try:
        symptomlog = SymptomLog.objects.filter(user=userprofile)
        if not symptomlog.exists():
            # Handle the case where no SymptomLog records are found
            # For example, you might want to create a default SymptomLog or provide a message
            return render(request, 'ChabotFeature/flowview.html', {
                'flows': Flow.objects.all(),
                'message': 'No symptom logs found for the user.'
            })
    except SymptomLog.DoesNotExist:
        # Handle any other issues with SymptomLog retrieval
        return render(request, 'ChabotFeature/flowview.html', {
            'flows': Flow.objects.all(),
            'message': 'Error retrieving symptom logs.'
        })

    # Retrieve all flows to display
    flows = Flow.objects.all()

    return render(request, 'ChabotFeature/flowview.html', {'flows': flows})



@login_required
# @login_required
def dashboard_view(request):
    return render(request, 'ChabotFeature/index.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        form = SignUpForm()
    return render(request, 'ChabotFeature/register.html', {'form': form})

@login_required
def get_flow_details(request, flow_id):
    try:
        # Get the flow object
        flow = Flow.objects.get(id=flow_id)
        
        # Get all steps associated with the flow
        steps = FlowStep.objects.filter(flow=flow).order_by('step_number')
        
        # Get user responses for these steps
        user_profile = UserProfile.objects.get(user=request.user)
        user_responses = UserResponse.objects.filter(user=user_profile, step__in=steps).values('step_id', 'response')

        # Get questions from FlowOption
        flow_options = FlowOption.objects.filter(step__in=steps).values('step_id', 'text')
        
        # Prepare response data
        step_data = {}
        for option in flow_options:
            step_id = option['step_id']
            if step_id not in step_data:
                step_data[step_id] = {
                    'questions': [],
                    'responses': ''
                }
            step_data[step_id]['questions'].append(option['text'])

        for response in user_responses:
            step_id = response['step_id']
            if step_id in step_data:
                step_data[step_id]['responses'] = response['response']

        response_data = {
            'success': True,
            'flow': {
                'id': flow.id,
                'name': flow.name,
                'description': flow.description,
                'steps': [
                    {
                        'id': step.id,
                        'step_number': step.step_number,
                        'questions': step_data.get(step.id, {}).get('questions', []),
                        'response': step_data.get(step.id, {}).get('responses', '')
                    }
                    for step in steps
                ]
            }
        }
        
    except Flow.DoesNotExist:
        response_data = {'success': False, 'error': 'Flow not found'}
    
    except UserProfile.DoesNotExist:
        response_data = {'success': False, 'error': 'UserProfile not found'}

    return JsonResponse(response_data)

    try:
        # Get the flow object
        flow = Flow.objects.get(id=flow_id)
        
        # Get all steps associated with the flow
        steps = FlowStep.objects.filter(flow=flow).order_by('step_number')
        
        # Get user responses for these steps
        user_profile = UserProfile.objects.get(user=request.user)
        user_responses = UserResponse.objects.filter(user=user_profile, step__in=steps).values('step_id', 'response')

        # Get questions from FlowOption
        flow_options = FlowOption.objects.filter(step__in=steps).values('step_id', 'text')
        # Prepare response data
        step_data = {}
        for option in flow_options:
            step_id = option['step_id']
            if step_id not in step_data:
                step_data[step_id] = {
                    'questions': [],
                    'responses': ''
                }
            step_data[step_id]['questions'].append(option['text'])

        for response in user_responses:
            step_id = response['step_id']
            if step_id in step_data:
                step_data[step_id]['responses'] = response['response']

        response_data = {
            'success': True,
            'flow': {
                'id': flow.id,
                'name': flow.name,
                'description': flow.description,
                'steps': [
                    {
                        'id': step.id,
                        'step_number': step.step_number,
                        'questions': step_data.get(step.id, {}).get('questions', []),
                        'response': step_data.get(step.id, {}).get('responses', '')
                    }
                    for step in steps
                ]
            }
        }
        
    except Flow.DoesNotExist:
        response_data = {'success': False, 'error': 'Flow not found'}
    
    except UserProfile.DoesNotExist:
        response_data = {'success': False, 'error': 'UserProfile not found'}

    return JsonResponse(response_data)



def flowcreate(request):
    return render(request, 'ChabotFeature/FlowCreate.html'  )
    
@csrf_exempt
def create_flow(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            flow_name = data.get('name')
            flow_description = data.get('description')
            steps_data = data.get('steps')
            
            flow = Flow.objects.create(name=flow_name, description=flow_description)
            step_mapping = {}
            
            for step_data in steps_data:
                step_number = len(step_mapping) + 1
                is_final_step = step_data.get('is_final_step', False)
                step = FlowStep.objects.create(flow=flow, step_number=step_number, text=step_data['text'], is_final_step=is_final_step)
                step_mapping[step_number] = step
                
                options_data = step_data.get('options', [])
                for option_data in options_data:
                    next_step_number = option_data.get('next_step')
                    next_step = step_mapping.get(next_step_number)
                    FlowOption.objects.create(step=step, text=option_data['text'], next_step=next_step)
            redirect("flowview")
            return JsonResponse({'message': 'Flow created successfully!'})
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required

def flow_view(request):
    flows = Flow.objects.all()
    return render(request, 'ChabotFeature/flowview.html', {'flows': flows})


@login_required

def edit_flow(request, flow_id):
    flow = get_object_or_404(Flow, id=flow_id)
    steps = FlowStep.objects.filter(flow=flow).prefetch_related('options')
    return render(request, 'ChabotFeature/edit_page.html', {'flow': flow, 'steps': steps})


@login_required
@csrf_exempt
def update_flow(request, flow_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        flow = get_object_or_404(Flow, id=flow_id)

        # Update flow
        flow.name = data['name']
        flow.description = data['description']
        flow.save()

        # Update steps and options
        for step_data in data['steps']:
            step = FlowStep.objects.get(id=step_data['id'])
            step.text = step_data['text']
            step.is_final_step = step_data['is_final_step']
            step.save()

            # Update options
            for option_data in step_data['options']:
                option = FlowOption.objects.get(id=option_data['id'])
                option.text = option_data['text']
                option.next_step_id = option_data['next_step']
                option.save()

        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request method'}, status=400)
@login_required
def respond_view(request, step_id, option_id):
    if request.method == 'GET':
        try:
            # Retrieve the current step and selected option
            step = get_object_or_404(FlowStep, id=step_id)
            selected_option = get_object_or_404(FlowOption, id=option_id)

            # Determine the next step (if exists)
            next_step = selected_option.next_step

            # Prepare response data for JSON
            if next_step:
                data = {
                    'text': next_step.text,
                    'step_id': next_step.id,
                    'options': [{'id': option.id, 'text': option.text} for option in next_step.options.all()],
                }
                
            else:
                # If it's the final step, no further options
                data = {
                    'text': "This is the final step.",
                    'step_id': None,
                    'options': [],
                }

            return JsonResponse(data)
        except FlowStep.DoesNotExist:
            return JsonResponse({'error': 'Step not found'}, status=404)
        except FlowOption.DoesNotExist:
            return JsonResponse({'error': 'Option not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required

def download_template(request):
    file_path = finders.find('ChabotFeature/template.xlsx')
    if file_path:
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=template.xlsx'
            return response
    else:
        return HttpResponse("File not found.", status=404)
@login_required

@csrf_exempt
def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        df = pd.read_excel(file)

        # Extract data
        data = {
            'flow_name': df['Flow Name'].iloc[0],
            'flow_description': df['Flow Description'].iloc[0],
            'steps': []
        }

        steps = df[['Step Number', 'Step Text', 'Is Final Step', 'Option Text', 'Next Step Number']]
        grouped = steps.groupby('Step Number')

        for step_number, group in grouped:
            step = {
                'text': group['Step Text'].iloc[0],
                'is_final_step': group['Is Final Step'].iloc[0] == 'True',
                'options': []
            }
            for _, row in group.iterrows():
                step['options'].append({
                    'text': row['Option Text'],
                    'next_step': row['Next Step Number']
                })
            data['steps'].append(step)

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required

def run_flow(request, flow_id):
    flow = get_object_or_404(Flow, id=flow_id)
    first_step = FlowStep.objects.filter(flow=flow).order_by('step_number').first()

    if not first_step:
        return render(request, 'ChabotFeature/error.html', {'message': 'No steps found for this flow'})

    # Pass the initial step to the template
    return render(request, 'ChabotFeature/run_flow.html', {
        'flow': flow,
        'step_id': first_step.id,
        'text': first_step.text,
        'options': list(first_step.options.values('id', 'text'))
    })
@login_required

def respond(request, step_id, option_id):
    try:
        step = FlowStep.objects.get(id=step_id)
        option = FlowOption.objects.get(id=option_id)

        # Get the next step
        next_step = FlowStep.objects.filter(flow=step.flow, step_number=option.next_step_number).first()

        if next_step:
            options = list(next_step.options.values('id', 'text'))
            response_data = {
                'step_id': next_step.id,
                'text': next_step.text,
                'options': options
            }
        else:
            response_data = {
                'text': 'Thank you for completing the flow!',
                'options': []
            }

        return JsonResponse(response_data)

    except FlowStep.DoesNotExist or FlowOption.DoesNotExist:
        return JsonResponse({'error': 'Invalid step or option ID'}, status=400)