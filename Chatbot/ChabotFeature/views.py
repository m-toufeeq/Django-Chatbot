from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import SignUpForm
from .models import *
from django.db.models import Prefetch
from django.views.decorators.http import require_POST
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.staticfiles import finders
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.middleware.csrf import get_token
import pandas as pd
import uuid
from django.db.models import Min
from django.db.models import Count

import random
import json
import pickle
import numpy as np
import nltk

from nltk.stem import WordNetLemmatizer
from keras.models import load_model


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
    
    # Retrieve the Flow object based on the button text
    try:
        flow = Flow.objects.get(id=flow_text)
    except Flow.DoesNotExist:
        return JsonResponse({'error': 'Flow not found'}, status=404)

    # Get the first step of the chosen flow
    first_step = FlowStep.objects.filter(flow=flow).order_by('step_number').first()

    if not first_step:
        return JsonResponse({'error': 'No steps found for this flow'}, status=404)

    # Generate a unique session ID and store it in the session
    session_id = str(uuid.uuid4())  # Generate unique session ID
    request.session['session_id'] = session_id

    # Return the first step of the flow along with the available options
    return JsonResponse({
        'step_id': first_step.id,
        'text': first_step.text,
        'options': list(first_step.options.values('id', 'text')),
        'session_id': session_id
    })
@login_required
def index(request):
    flow = Flow.objects.all()
    return redirect('dashboard')




#-----------------------------
# Conversational Chatbot Code start from here
#-----------------------------



# Load model and data
lemmatizer = WordNetLemmatizer()
intents = json.loads(open('ChabotFeature/static/gynae/intents_gynae.json').read())
words = pickle.load(open('ChabotFeature/static/gynae/words.pkl', 'rb'))
classes = pickle.load(open('ChabotFeature/static/gynae/classes.pkl', 'rb'))
model = load_model('ChabotFeature/static/gynae/gynae_chatbot_model.h5')


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list


def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    result = "Oops, I don't understand you! Try using different words."
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result


# View for rendering chatbot page
def Converstational_flowview(request):
    return render(request, 'ChabotFeature/conversational_flow.html')


# View to handle AJAX requests
def get_chatbot_response(request):
    message = request.GET.get('message')
    ints = predict_class(message)
    res = get_response(ints, intents)
    return JsonResponse({'response': res})



#-----------------------------------
# Conversational Chat ends here
#-----------------------------------

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
@require_POST
def create_flow(request):
    try:
        data = json.loads(request.body)
        flow_name = data.get('name')
        flow_description = data.get('description')
        steps = data.get('steps', [])
        # Create Flow
        flow = Flow.objects.create(name=flow_name, description=flow_description)
        
        print(data)
        # Create FlowSteps and store them in a dictionary for later reference
        step_map = {}
        for step_data in steps:
            step_number = step_data.get('step_number')
            step_text = step_data.get('text')
            is_final_step = step_data.get('is_final_step', False)

            # Create FlowStep
            step = FlowStep.objects.create(
                flow=flow,
                step_number=step_number,
                text=step_text,
                is_final_step=is_final_step
            )

            # Store the created FlowStep in the map
            step_map[step_number] = step

        # Create FlowOptions using the stored FlowSteps
        for step_data in steps:
            step_number = step_data.get('step_number')
            step = step_map.get(step_number)
            options = step_data.get('options', [])
            
            for option_data in options:
                option_text = option_data.get('text')
                next_step_number = option_data.get('next_step_number')

                # Determine the next step instance
                

                next_step = None
                if next_step_number:
                    next_step = FlowStep.objects.get(step_number=next_step_number, flow=flow)

                # Create FlowOption
                FlowOption.objects.create(
                    step=step,
                    text=option_text,
                    next_step=next_step
                )
                

        return JsonResponse({'message': 'Flow created successfully!'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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
            print(step.text)
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

            # Retrieve the session ID from the request session
            session_id = request.session.get('session_id', None)
            if not session_id:
                return JsonResponse({'error': 'Session not found'}, status=400)

            # Store user response with the session ID
            user_response = UserResponse.objects.create(
                user=UserProfile.objects.get(user=request.user),
                step=step,
                response=selected_option.text,
                session_id=session_id
            )

            # Prepare response data for JSON
            if next_step:
                data = {
                    'text': next_step.text,
                    'step_id': next_step.id,
                    'options': [{'id': option.id, 'text': option.text} for option in next_step.options.all()],
                }
            else:
                # If it's the final step, clear the session and return final message
                request.session.pop('session_id', None)  # End session
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
@csrf_exempt
def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        df = pd.read_excel(file)

        # Validate the columns
        required_columns = ['Flow Name', 'Flow Description', 'Step Number', 'Step Text', 'Is Final Step', 'Option Text', 'Next Step Number']
        if not all(col in df.columns for col in required_columns):
            return JsonResponse({'error': 'Invalid columns in the uploaded file. Compare your columns with the template!'}, status=400)

        def is_valid_step_number(value):
            if isinstance(value, str) and value == '-':
                return True
            try:
                int(value)
                return True
            except (ValueError, TypeError):
                return False

        if not df['Step Number'].apply(is_valid_step_number).all():
            return JsonResponse({'error': 'The column "Step Number" must contain integers or "-".'}, status=400)
        if not df['Next Step Number'].apply(is_valid_step_number).all():
            return JsonResponse({'error': 'The column "Next Step Number" must contain integers or "-".'}, status=400)
        
        def normalize_boolean(value):
            value = str(value)
            if isinstance(value, str):
                if value.strip().lower() in ['true', 't', 'yes', '1']:
                    return True
                elif value.strip().lower() in ['false', 'f', 'no', '0']:
                    return False
            return None


        normalized_is_final_step = df['Is Final Step'].apply(normalize_boolean)

        # Check for any invalid boolean entries
        if normalized_is_final_step.isnull().any():
            return JsonResponse({'error': 'The column "Is Final Step" must contain boolean values (true/false/0/1/yes/no).'}, status=400)

        # Replace the original 'Is Final Step' column with normalized values
        df['Is Final Step'] = normalized_is_final_step

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
                'is_final_step': bool(group['Is Final Step'].iloc[0]),  # This is now guaranteed to be True/False
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


    # Generate a unique session ID and store it in the session
    session_id = str(uuid.uuid4())  # Generate unique session ID
    request.session['session_id'] = session_id


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

def upload_flow(request):
    return render(request, 'ChabotFeature/upload_flow.html')

@login_required
def skip_step(request, step_id):
    # Get the current step
    current_step = get_object_or_404(FlowStep, id=step_id)
    UserResponse.objects.create(
        user=UserProfile.objects.get(user=request.user),
        step=current_step,
        response="skip"
    )
    # Find the next step in the flow
    next_step = FlowStep.objects.filter(flow=current_step.flow, step_number__gt=current_step.step_number).order_by('step_number').first()
    
    if not next_step:
        return JsonResponse({'error': 'No further steps available'}, status=404)

    # Return the next step of the flow along with the available options
    return JsonResponse({
        'step_id': next_step.id,
        'text': next_step.text,
        'options': list(next_step.options.values('id', 'text'))
    })

@login_required
def exit_flow(request):
    session_id = request.session.pop('session_id', None)
    if session_id:
        return JsonResponse({'message': 'Flow exited successfully. Your session has ended.'})
    return JsonResponse({'error': 'No active session found.'}, status=400)

@login_required
def get_flow_steps(request):
    flow_id = request.GET.get('flow_id')
    session_id = request.GET.get('session_id')

    flow = Flow.objects.get(id=flow_id)
    steps = flow.flowstep_set.all().order_by('step_number')
    user_responses = UserResponse.objects.filter(session_id=session_id, step__flow=flow)

    steps_data = []
    for step in steps:
        user_response = user_responses.filter(step=step).first()
        steps_data.append({
            'text': step.text,
            'user_response': user_response.response if user_response else None
        })

    return JsonResponse({'steps': steps_data})

@login_required
def user_responses(request):
    user_profile = request.user.userprofile

    # Fetch the first response per unique session_id
    unique_sessions = (
        UserResponse.objects
        .filter(user=user_profile)
        .values('session_id')  # Group by session_id
        .annotate(first_response_date=Min('response_date'))  # Get the earliest response per session
        .order_by('first_response_date')
    )
    # Fetch the corresponding flow and step data
    responses = []
    for session in unique_sessions:
        # Get the first UserResponse for the session to display in the table
        response = UserResponse.objects.filter(
            user=user_profile, session_id=session['session_id']
        ).order_by('response_date').first()
        responses.append(response)

    context = {
        'responses': responses,
    }
    
    return render(request, 'ChabotFeature/user_responses.html', context)
