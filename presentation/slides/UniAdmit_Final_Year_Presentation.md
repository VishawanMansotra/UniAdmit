# UniAdmit — Final Year Project Presentation (Undergraduate)

## Presentation defaults used
- Duration target: 12 minutes + 3 minutes Q&A
- Format: individual presenter
- Audience: faculty panel (technical, with brief non-technical framing)
- Emphasis split: core admission workflow (70%), AI chatbot (30%)

---

## Slide 1 — Title
- **UniAdmit: Smart Undergraduate Admission Management System**
- Student name, roll no., department
- Guide/Supervisor, institution, academic session

## Slide 2 — Problem Statement & Motivation
- Traditional admission process is fragmented, manual, and slow
- Difficult tracking for students and admin
- Need for centralized, transparent, and guided admission workflow

## Slide 3 — Objectives & Scope
- Digitize end-to-end admission workflow
- Role-based experience for students and administrators
- Add AI support for common admission queries
- Out of scope: multi-college federation, mobile-native app, advanced analytics

## Slide 4 — Existing vs Proposed Workflow
- Existing: offline forms + manual verification + delayed updates
- Proposed: web portal with OTP onboarding, digital submission, live status, admin control
- Outcome: lower turnaround time and better communication

## Slide 5 — System Overview & Roles
- **Student:** register, verify OTP, apply, pay, track status
- **Admin:** review applications, control rounds, publish merit PDFs, export CSV
- **AI Assistant:** answers FAQs, captures unresolved questions, receives feedback

## Slide 6 — Technology Stack
- Backend: Django (Python)
- Database config: `dj-database-url` (MySQL in deployment, configurable)
- Payments: Razorpay integration
- AI: Google Gemini (`google-generativeai`)
- PDF generation: ReportLab
- Frontend: Django templates + Bootstrap + static CSS

## Slide 7 — High-Level Architecture
- Django project (`admission`) with two apps: `core`, `chatbot`
- Request flow: Browser → Django Views → Models/DB → Payment/AI services
- Output channels: UI screens, generated PDFs, chatbot API responses
- (Use `presentation/assets/architecture_diagram.mmd`)

## Slide 8 — Data Model Overview
- `core`: `StudentProfile`, `Application`, `Course`, `AdmissionRound`, `Payment`, `MeritListPDF`
- `chatbot`: `CollegeKnowledge`, `ChatSession`, `ChatMessage`, `ChatFeedback`, `UnansweredQuery`
- Relationship focus: student-to-application, application-to-payment, chatbot session-to-messages

## Slide 9 — Key Feature Set
- OTP-based registration and verification
- Round-aware admission control (`closed`, `round1_jee`, `round2_cuet`, `round3_board`)
- Application management with document handling
- Payment initiation and verification flow
- Merit list publication/download + CSV export
- AI chatbot knowledge management and feedback loop

## Slide 10 — Student Journey (Screen Sequence)
- Home → Register → Verify OTP → Login → Dashboard
- Profile update → Apply (details + documents) → Payment
- My Applications / Status tracking
- (Insert screenshots: home, dashboard, apply)

## Slide 11 — Admin Journey (Screen Sequence)
- Admin login → Admin dashboard
- View/filter applications + application detail review
- Set active admission round
- Upload/publish merit PDFs and export CSV
- (Insert screenshot: admin dashboard)

## Slide 12 — AI Chatbot Design
- Knowledge source: active entries in `CollegeKnowledge`
- Prompting with behavior constraints and context formatting
- Session + message history for continuity
- Quality loop: `UnansweredQuery` + `ChatFeedback`

## Slide 13 — Security & Validation Controls
- OTP validity window (5 minutes)
- Allowed registration email domain checks
- Auth-protected dashboard/admin routes
- Payment verification before confirmation workflows
- Input validation via Django forms/models

## Slide 14 — Methodology & Validation
- Requirements analysis → design → implementation → testing
- Verified test run: `python manage.py test` (21 tests passed)
- Validation through student/admin/chatbot use-case walkthrough

## Slide 15 — Outcomes & Benefits
- Centralized admission lifecycle
- Faster processing and improved transparency
- Better applicant support via integrated chatbot
- Structured admin controls for rounds/results

## Slide 16 — Challenges & Resolutions
- Multi-step admission flow consistency → model/view separation
- Balancing chatbot flexibility with factual accuracy → database-backed knowledge
- Handling uncertainty in chatbot responses → unresolved query tracking and feedback review

## Slide 17 — Limitations, Ethics & Future Enhancements
- Limitations: no mobile app, no advanced predictive analytics yet
- Ethics: controlled handling of student data, no fabricated chatbot claims
- Future: notifications, analytics dashboard, role expansion, stronger AI grounding

## Slide 18 — Live Demo Plan, Conclusion & Q&A
- Demo path: register/login → apply → admin controls → chatbot feedback cycle
- Backup strategy: screenshot/video fallback for network/API/payment disruptions
- Closing: UniAdmit as a practical, extensible admission automation platform

