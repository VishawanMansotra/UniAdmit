import google.generativeai as genai
from django.conf import settings
from .models import CollegeKnowledge, UnansweredQuery, ChatSession, ChatMessage

# ─────────────────────────────────────────────
#  Configure Gemini once when server starts
# ─────────────────────────────────────────────
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


# ─────────────────────────────────────────────
#  Build knowledge base from your database
# ─────────────────────────────────────────────
def build_knowledge_base():
    """
    Fetches all active knowledge entries from database
    and formats them into a text block for the AI.
    
    This is how you "train" the chatbot —
    whatever you add to CollegeKnowledge model,
    the chatbot will know it automatically.
    """
    knowledge_entries = CollegeKnowledge.objects.filter(is_active=True).order_by('category')

    if not knowledge_entries.exists():
        return "No specific college knowledge available yet."

    knowledge_text = ""
    current_category = None

    for entry in knowledge_entries:
        # Group by category for clean formatting
        if entry.category != current_category:
            current_category = entry.category
            knowledge_text += f"\n\n=== {entry.get_category_display().upper()} ===\n"

        knowledge_text += f"\n• {entry.topic}:\n  {entry.information}\n"

    return knowledge_text


# ─────────────────────────────────────────────
#  Build system prompt with knowledge base
# ─────────────────────────────────────────────
def build_system_prompt():
    """
    Creates the full prompt that tells Gemini:
    1. Who it is (UniAdmit Assistant)
    2. What it knows (your college knowledge base)
    3. How to behave
    """
    knowledge_base = build_knowledge_base()

    system_prompt = f"""
You are UniAdmit Assistant, the official AI chatbot for UIET (University Institute of Engineering & Technology), 
University of Jammu. You help students and parents with queries related to admissions, courses, campus life, 
facilities, and anything related to the college.

════════════════════════════════════════
COLLEGE KNOWLEDGE BASE (Use this to answer):
════════════════════════════════════════
{knowledge_base}

════════════════════════════════════════
YOUR BEHAVIOR RULES:
════════════════════════════════════════
1. Always be polite, helpful, and professional.
2. Answer ONLY based on the knowledge base provided above.
3. If a question is not covered in the knowledge base, say:
   "I don't have specific information about that right now. 
    Please contact the admission office directly at [college contact]."
4. Keep answers concise and easy to understand.
5. Use simple English — students may not be fluent.
6. If someone asks about their application status, tell them to:
   Login → Dashboard → Check Application Status.
7. Never make up information. Only use what is in the knowledge base.
8. For greetings, respond warmly and ask how you can help.
9. Format answers clearly using bullet points when listing multiple items.
10. Always end with "Is there anything else I can help you with?"

Remember: You represent UIET, University of Jammu. Be professional and helpful at all times.
"""
    return system_prompt


# ─────────────────────────────────────────────
#  Main chat function
# ─────────────────────────────────────────────
def get_ai_response(user_message, conversation_history=None, session=None):
    """
    Sends user message to Gemini and returns AI response.
    
    Args:
        user_message: The student's question
        conversation_history: List of previous messages in this session
        session: ChatSession object (optional)
    
    Returns:
        dict: { 'response': str, 'success': bool, 'error': str or None }
    """
    try:
        system_prompt = build_system_prompt()

        # Build conversation messages for Gemini
        # Gemini needs alternating user/model messages
        messages = []

        # Add conversation history if exists (for follow-up questions)
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 6 messages only (save tokens)
                if msg['sender'] == 'user':
                    messages.append({
                        "role": "user",
                        "parts": [msg['message']]
                    })
                else:
                    messages.append({
                        "role": "model",
                        "parts": [msg['message']]
                    })

        # Start chat with history
        chat = model.start_chat(history=messages)

        # Combine system prompt with user message
        full_message = f"{system_prompt}\n\nStudent Question: {user_message}"

        # Get response from Gemini
        response = chat.send_message(full_message)
        bot_response = response.text

        # Check if response seems like "I don't know"
        # If so, log it as unanswered query for admin to review
        low_confidence_phrases = [
            "don't have specific information",
            "not covered",
            "contact the admission office",
            "i'm not sure",
            "i don't know"
        ]
        is_unanswered = any(phrase in bot_response.lower() for phrase in low_confidence_phrases)

        if is_unanswered and session:
            # Log unanswered query so admin can add it to knowledge base
            existing = UnansweredQuery.objects.filter(
                query__icontains=user_message[:50]
            ).first()

            if existing:
                existing.frequency += 1
                existing.save()
            else:
                UnansweredQuery.objects.create(
                    query=user_message,
                    session=session
                )

        return {
            'response': bot_response,
            'success': True,
            'error': None,
            'is_unanswered': is_unanswered
        }

    except Exception as e:
        error_message = str(e)

        # Handle specific Gemini API errors
        if "API_KEY" in error_message.upper():
            return {
                'response': "Chatbot configuration error. Please contact admin.",
                'success': False,
                'error': "Invalid API Key"
            }
        elif "quota" in error_message.lower() or "limit" in error_message.lower():
            return {
                'response': "I'm currently busy. Please try again in a moment.",
                'success': False,
                'error': "Rate limit exceeded"
            }
        else:
            return {
                'response': "Sorry, I encountered an error. Please try again.",
                'success': False,
                'error': error_message
            }


# ─────────────────────────────────────────────
#  Session helpers
# ─────────────────────────────────────────────
def get_or_create_session(request):
    """Get existing session or create a new one"""
    import uuid

    session_id = request.session.get('chatbot_session_id')

    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['chatbot_session_id'] = session_id

    session, created = ChatSession.objects.get_or_create(session_id=session_id)
    return session


def get_conversation_history(session):
    """Get last N messages from session for context"""
    messages = ChatMessage.objects.filter(
        session=session
    ).order_by('-timestamp')[:10]  # Last 10 messages

    # Reverse to get chronological order
    history = []
    for msg in reversed(messages):
        history.append({
            'sender': msg.sender,
            'message': msg.message
        })

    return history
