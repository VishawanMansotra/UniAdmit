# 8-Minute Speaking Version

## 1) Problem and need
Admissions are often delayed due to manual data handling, disconnected updates, and repetitive student queries. This creates stress for both students and administrators.

## 2) Project objective
UniAdmit provides one platform for the complete admission lifecycle: registration, verification, application, payment, status, and results communication.

## 3) System design
The project uses Django with:
- `core` app for student/admin workflows
- `chatbot` app for AI support and feedback-driven improvement

## 4) Key student flow
Students register, verify OTP, log in, update profile, submit an application, and complete payment verification. They can then track their status in dashboard views.

## 5) Key admin flow
Admins can view applications, control the active admission round, publish merit list PDFs, and export CSV records.

## 6) AI chatbot flow
The chatbot uses a curated knowledge base, session history, and controlled response behavior. If confidence is low, unresolved queries are stored for admin review. Feedback ratings help improve future responses.

## 7) Validation and impact
Testing was executed via Django test suite. The portal improves transparency, response time, and process control while maintaining a clean modular architecture.

## 8) Future scope
Planned improvements include mobile-first support, analytics dashboards, richer notifications, and stronger AI grounding/governance.
