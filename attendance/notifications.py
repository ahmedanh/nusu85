"""Helpers for pushing real-time notifications over Channels."""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def push_notification(user_id, title, body, level='info'):
    """Send a real-time notification to a specific user."""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{user_id}',
            {'type': 'notification_message', 'title': title,
             'body': body, 'level': level}
        )
    except Exception:
        pass  # Graceful degradation if channels not running


def push_gate_event(student_name, student_code, status, room=None):
    """Broadcast a gate entry event to all gate staff."""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'gate_live',
            {'type': 'gate_entry', 'student_name': student_name,
             'student_code': student_code, 'status': status,
             'room': room or ''}
        )
    except Exception:
        pass
