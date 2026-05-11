import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .models import ChatMessage, ChatFeedback, CollegeKnowledge
from .utils import get_ai_response, get_or_create_session, get_conversation_history


# ─────────────────────────────────────────────
#  Main Chat API Endpoint
# ─────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """
    POST /chatbot/api/chat/
    Body: { "message": "What are the fees for CSE?" }
    Returns: { "response": "...", "success": true }
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        if len(user_message) > 500:
            return JsonResponse({'error': 'Message too long (max 500 characters)'}, status=400)

        # Get or create chat session
        session = get_or_create_session(request)

        # Get conversation history for context
        history = get_conversation_history(session)

        # Save user message to DB
        ChatMessage.objects.create(
            session=session,
            sender='user',
            message=user_message
        )

        # Get AI response from Gemini
        result = get_ai_response(user_message, history, session)

        # Save bot response to DB
        bot_msg_obj = ChatMessage.objects.create(
            session=session,
            sender='bot',
            message=result['response']
        )

        return JsonResponse({
            'response': result['response'],
            'success': result['success'],
            'message_id': bot_msg_obj.id,  # Used for feedback
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ─────────────────────────────────────────────
#  Feedback API
# ─────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def feedback_api(request):
    """
    POST /chatbot/api/feedback/
    Body: { "message_id": 5, "rating": 3, "comment": "Very helpful!" }
    """
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        rating = data.get('rating')

        if not message_id or not rating:
            return JsonResponse({'error': 'message_id and rating required'}, status=400)

        message = ChatMessage.objects.get(id=message_id, sender='bot')

        ChatFeedback.objects.update_or_create(
            message=message,
            defaults={
                'rating': rating,
                'comment': data.get('comment', '')
            }
        )

        return JsonResponse({'success': True, 'message': 'Feedback saved!'})

    except ChatMessage.DoesNotExist:
        return JsonResponse({'error': 'Message not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ─────────────────────────────────────────────
#  Get Chat History
# ─────────────────────────────────────────────
def chat_history_api(request):
    """
    GET /chatbot/api/history/
    Returns last 20 messages in current session
    """
    session = get_or_create_session(request)
    messages = ChatMessage.objects.filter(session=session).order_by('timestamp')[:20]

    history = [{
        'sender': msg.sender,
        'message': msg.message,
        'timestamp': msg.timestamp.strftime('%I:%M %p')
    } for msg in messages]

    return JsonResponse({'history': history})


# ─────────────────────────────────────────────
#  Clear Chat Session
# ─────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def clear_chat_api(request):
    """
    POST /chatbot/api/clear/
    Clears current session so new conversation starts
    """
    if 'chatbot_session_id' in request.session:
        del request.session['chatbot_session_id']

    return JsonResponse({'success': True, 'message': 'Chat cleared!'})
