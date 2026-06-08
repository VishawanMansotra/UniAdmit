# Verified Factual Data Points for Slides

- Programs represented in project: CSE, Civil, ECE (3 programs)
- Default seats per course model: 60 (`Course.total_seats`, `available_seats` default)
- Admission round states: closed, round1_jee, round2_cuet, round3_board
- OTP validity configured: 300 seconds
- Payment amount configured: `PAYMENT_AMOUNT = 50000` paise (₹500)
- Main apps: `core`, `chatbot`
- Major core models: 6 (`StudentProfile`, `Course`, `AdmissionRound`, `Application`, `Payment`, `MeritListPDF`)
- Major chatbot models: 5 (`CollegeKnowledge`, `ChatSession`, `ChatMessage`, `ChatFeedback`, `UnansweredQuery`)
- Test status during preparation: `python manage.py test` passed (21 tests)

## Source paths
- `/tmp/workspace/VishawanMansotra/UniAdmit/core/models.py`
- `/tmp/workspace/VishawanMansotra/UniAdmit/admission/settings.py`
- `/tmp/workspace/VishawanMansotra/UniAdmit/core/views.py`
- `/tmp/workspace/VishawanMansotra/UniAdmit/chatbot/models.py`
