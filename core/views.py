from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
import json 
from django.http import JsonResponse
from agent.agent import get_agent_response
from agent.parser import parse_response , validate_action
from agent.tools import  execute_action
User = get_user_model() 

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').lower()
        
        try:
            user = User.objects.get(email=email)
            auth_login(request, user)
            request.session['email'] = user.email
            request.session['username'] = user.username
            return redirect('chatbot')

        except User.DoesNotExist:
            messages.error(request, 'Email not found.')
    return render(request, 'login.html', {'error': messages.get_messages(request)})

@require_POST 
def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def database_view(request):
    users = User.objects.all().values(
        'username', 'email', 'name', 'good_name', 'dob', 'city', 'company' , 'phone'
    )
    return render(request, 'database.html', {'users': users})


@login_required
def chatbot_view(request):
    return render(request, 'chatbot.html')


@login_required
@require_POST
def chatbot_api(request):
    try:
        
        # Parse request body
        data = json.loads(request.body)
        user_input = data.get('message', '').strip()
        
        if not user_input:
            print("DEBUG: Empty message, returning error")
            return JsonResponse({
                'success': False,
                'type': 'error',
                'message': 'Please enter a message'
            })
        
        #Get AI response
        agent_response = get_agent_response(user_input)
        
        #Check for AI errors
        if '"error"' in agent_response or agent_response.startswith('{"error"'):
            return JsonResponse({
                'success': False,
                'type': 'error',
                'message': f'AI Error: {agent_response}'
            })
        
        #Parse JSON
        parsed_json = parse_response(agent_response)
        
        #Check parsing errors
        if 'error' in parsed_json:
            return JsonResponse({
                'success': False,
                'type': 'error',
                'message': f"Parse Error: {parsed_json['error']}"
            })
        # Validate action
        is_valid, error_msg = validate_action(parsed_json)
        if not is_valid:
            return JsonResponse({
                'success': False,
                'type': 'error',
                'message': f'Validation Error: {error_msg}'
            })
        result = execute_action(parsed_json)
        response_type = result.get('type', 'database_action')
        if result.get('success'):
            return JsonResponse({
                'success': True,
                'type': response_type,
                'message': result.get('message', 'Operation completed'),
                'show_database': result.get('show_database', False)
            })
        else:
            return JsonResponse({
                'success': False,
                'type': 'error',
                'message': result.get('message', 'Operation failed')
            })
            
    except json.JSONDecodeError as e:
        return JsonResponse({
            'success': False,
            'type': 'error',
            'message': 'Invalid JSON in request'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'type': 'error',
            'message': f'Server error: {str(e)}'
        })

