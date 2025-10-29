import json
import re
from typing import Dict, Tuple


def parse_response(text: str) -> Dict:
    try:
        text = text.strip()
        if text.startswith('```'):
            lines = text.split('\n')
            lines = lines[1:] 
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            text = '\n'.join(lines)
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            parsed = json.loads(json_str)
            if 'type' not in parsed:
                return {'error': 'Missing required field: type'}
            if parsed['type'] not in ['conversation', 'database_view', 'database_action']:
                return {'error': f'Invalid type: {parsed["type"]}'}
            if parsed['type'] == 'conversation':
                if 'message' not in parsed:
                    return {'error': 'Conversation type requires message field'}
            elif parsed['type'] in ['database_view', 'database_action']:
                if 'action' not in parsed:
                    return {'error': 'Database operations require action field'}
                if parsed['action'] not in ['create', 'read', 'update', 'delete']:
                    return {'error': f'Invalid action: {parsed["action"]}'}
            if 'filter' not in parsed:
                parsed['filter'] = {}
            if 'data' not in parsed:
                parsed['data'] = {}
            if 'message' not in parsed:
                parsed['message'] = ''
            return parsed
        else:
            return {'error': 'No valid JSON found in response'}
    except json.JSONDecodeError as e:
        return {'error': f'Invalid JSON format: {str(e)}'}
    except Exception as e:
        return {'error': f'Error parsing response: {str(e)}'}


def validate_action(parsed_json: Dict) -> Tuple[bool, str]:
    if 'error' in parsed_json:
        return False, parsed_json['error']
    response_type = parsed_json.get('type')
    if response_type == 'conversation':
        if not parsed_json.get('message'):
            return False, 'Conversation response missing message'
        return True, None
    if response_type in ['database_view', 'database_action']:
        action = parsed_json.get('action')
        data = parsed_json.get('data', {})
        filter_dict = parsed_json.get('filter', {})
        if action == 'create':
            if not data.get('username') or not data.get('email'):
                return False, 'Create action requires username and email'
        if action == 'update':
            if not data:
                return False, 'Update action requires data to update'
        if action == 'delete':
            if not filter_dict:
                return False, 'Delete action requires a filter (cannot delete all users)'
    
    return True, None