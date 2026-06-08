# Full-Length Speaking Version (12 Minutes)

## Opening
Good morning/afternoon. I am presenting **UniAdmit**, an undergraduate final-year project designed to automate and modernize the admission process.

## Problem context
Traditional admissions rely on manual coordination, disconnected updates, and repetitive communication. Students struggle to know what to do next, and administrators handle high operational overhead.

## Objective
Our objective was to create a practical platform that supports:
1. Guided student onboarding and application,
2. Administrative control and transparency,
3. AI-assisted query support.

## Architecture overview
UniAdmit is built on Django. The `core` app handles admissions logic, and the `chatbot` app handles AI interactions. Data is persisted in relational models, with optional external integrations for payments and AI responses.

## Student-side flow
Students register, verify OTP, and log in. From dashboard, they can edit profile and submit applications with relevant details/documents. Payment is initiated and verified. Students can later monitor status and related outputs.

## Admin-side flow
Admins use dedicated dashboard actions to review applications, control active admission round, publish merit PDFs, and export CSV data for reporting and operations.

## AI assistant design
The chatbot relies on managed knowledge entries. It maintains session context and provides concise responses. If a question is not handled well, it is recorded in an unanswered queue. Users can also rate chatbot responses, creating a continuous quality loop.

## Security and validation
The project applies OTP expiry constraints, allowed-domain checks during registration, authenticated routes for protected pages, and payment verification before confirmations. Model/form validation supports data integrity.

## Testing and validation
The system is validated through the existing Django test suite and end-to-end feature walkthroughs for student, admin, and chatbot scenarios.

## Outcomes
UniAdmit improves process visibility, speeds up communication, and centralizes control. It is especially suitable for institutions handling repeated admission cycles with limited staff bandwidth.

## Limitations
Current version does not include native mobile apps, advanced analytics, or multi-institution tenancy.

## Future enhancements
Future roadmap includes analytics dashboards, role expansion, improved notification channels, and stronger AI grounding mechanisms.

## Closing
In summary, UniAdmit is a practical and extensible admission automation platform that addresses real operational pain points while remaining academically sound for final-year evaluation.
