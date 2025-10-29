from django.contrib.auth import get_user_model
from typing import Dict
User = get_user_model()
DEFAULT_PASSWORD = 'defaultpassword123'

def normalize_data(data:Dict) -> Dict:
    normalized = {}
    preserver_case_fields = {'bio'}
    for key, value in data.items():
        if value is None:
            normalized[key] = value
        elif key in preserver_case_fields:
            normalized[key] = value
        elif isinstance(value, str):
            normalized[key] = value.lower()
        else:
            normalized[key] = value
    return normalized

def read_users(filter_dict: Dict) -> Dict:
    try:
        if filter_dict:
            filter_dict = normalize_data(filter_dict)
        queryset = User.objects.all()
        if filter_dict:
            queryset = queryset.filter(**filter_dict)
        users = queryset.values(
            'username', 'email', 'name', 'good_name', 
            'dob', 'city', 'company', 'bio', 'phone', 'gender'
        )
        user_list = list(users)
        count = len(user_list)
        if count == 0:
            return {'success': True, 'message': 'No users found matching the criteria'}
        user_info = []
        for user in user_list:
            info_parts = [
                f"👤 Username: {user['username']}",
                f"📧 Email: {user['email']}"
            ]
            field_icons = {
                'name': '📝', 'good_name': '✨', 'city': '🏙️',
                'company': '🏢', 'dob': '📅', 'phone': '📱',
                'gender': '⚧', 'bio': '📖'
            }
            for field, icon in field_icons.items():
                if user.get(field):
                    info_parts.append(f"{icon} {field.replace('_', ' ').title()}: {user[field]}")
            user_info.append("\n".join(info_parts))
        if count == 1:
            message = f"Found user information:\n\n{user_info[0]}"
        else:
            message = f"Found {count} user(s):\n\n" + "\n\n".join(user_info)
        return {'success': True, 'message': message}
    except Exception as e:
        return {'success': False, 'message': f'Error reading users: {str(e)}'}

def create_user(data: Dict) -> Dict:
    try:
        data = normalize_data(data)
        username = data.get('username')
        email = data.get('email')
        
        # Check if trying to create a superuser
        if data.get('is_superuser'):
            return {
                'success': False, 
                'message': '❌ Cannot create superuser accounts through this interface. Superuser accounts must be created through Django admin.'
            }
        
        if User.objects.filter(username=username).exists():
            return {'success': False, 'message': f'Username "{username}" already exists'}
        
        if User.objects.filter(email=email).exists():
            return {'success': False, 'message': f'Email "{email}" already exists'}
        user = User.objects.create_user(
            username=username,
            email=email,
            password=DEFAULT_PASSWORD
        )
        optional_fields = ['name', 'good_name', 'dob', 'city', 'company', 'bio', 'phone', 'gender']
        for field in optional_fields:
            if field in data:
                setattr(user, field, data[field])
        user.save()
        return {
            'success': True,
            'message': f'✅ User "{username}" created successfully with email "{email}"'
        }
    except Exception as e:
        return {'success': False, 'message': f'Error creating user: {str(e)}'}

def update_user(filter_dict: Dict, data: Dict) -> Dict:
    try:
        if not filter_dict:
            return {'success': False, 'message': 'Filter required for update operation'}
        filter_dict = normalize_data(filter_dict)
        data = normalize_data(data)
        queryset = User.objects.filter(**filter_dict)
        count = queryset.count()
        if count == 0:
            return {'success': False, 'message': 'No users found matching the criteria'}
        
        # Check if trying to modify superuser status
        if 'is_superuser' in data:
            return {
                'success': False, 
                'message': '❌ Cannot modify superuser status. This field is protected for security reasons.'
            }
        
        usernames = ', '.join(queryset.values_list('username', flat=True))
        queryset.update(**data)
        return {'success': True, 'message': f'✅ Updated {count} user(s): {usernames}'}
    except Exception as e:
        return {'success': False, 'message': f'Error updating users: {str(e)}'}


def delete_user(filter_dict: Dict) -> Dict:
    try:
        if not filter_dict:
            return {'success': False, 'message': 'Filter required for delete operation'}
        filter_dict = normalize_data(filter_dict)
        queryset = User.objects.filter(**filter_dict)
        count = queryset.count()
        if count == 0:
            return {'success': False, 'message': 'No users found matching the criteria'}
        
        # Check if any of the users to be deleted are superusers
        superusers = queryset.filter(is_superuser=True)
        if superusers.exists():
            superuser_names = ', '.join(superusers.values_list('username', flat=True))
            return {
                'success': False, 
                'message': f'❌ Cannot delete superuser(s): {superuser_names}. Superusers cannot be deleted for security reasons.'
            }
        
        usernames = ', '.join(queryset.values_list('username', flat=True))
        queryset.delete()
        return {'success': True, 'message': f'✅ Deleted {count} user(s): {usernames}'}
    except Exception as e:
        return {'success': False, 'message': f'Error deleting users: {str(e)}'}

def execute_action(parsed_json:Dict) ->Dict:
    response_type = parsed_json.get('type')
    if response_type == 'conversation':
        return {'success': 'true', 'type': 'conversation', 'message': parsed_json.get('message', 'How can I help you?')}
    if response_type == 'database_view':
        result = read_users(parsed_json.get('filter', {}))
        result['type'] = 'database_view'
        result['show_database'] = True
        return result
    if response_type == 'database_action':
        action = parsed_json.get('action')
        
        if action == 'create':
            result = create_user(parsed_json.get('data', {}))
        elif action == 'update':
            result = update_user(parsed_json.get('filter', {}), parsed_json.get('data', {}))
        elif action == 'delete':
            result = delete_user(parsed_json.get('filter', {}))
        else:
            result = {'success': False, 'message': f'Unknown action: {action}'}
        
        result['type'] = 'database_action'
        return result
    
    return {'success': False, 'message': f'Unknown response type: {response_type}'}



