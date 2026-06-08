# Viva Q&A Cheat Sheet

## Architecture
**Q:** Why split into `core` and `chatbot` apps?
**A:** Separation of concerns. Admission workflows and AI workflows evolve independently while sharing the same project and authentication context.

## Database design
**Q:** Why separate `StudentProfile` from auth user?
**A:** Keeps Django auth model clean and stores domain-specific profile fields separately.

## Admissions logic
**Q:** How do rounds work?
**A:** `AdmissionRound` controls active phase (`closed`, `round1_jee`, `round2_cuet`, `round3_board`) and the apply workflow reacts accordingly.

## Payment
**Q:** How is payment handled safely?
**A:** Payment initiation stores order references and verification updates status before confirmation outputs.

## Chatbot quality
**Q:** How do you prevent hallucination?
**A:** Responses are guided by internal knowledge base and behavior rules; unresolved/low-confidence queries are tracked.

## Security
**Q:** What student-data protections are present?
**A:** Auth-gated pages, OTP verification, validation layers, and controlled admin operations.

## Testing
**Q:** How was reliability checked?
**A:** Existing Django test suite was executed successfully; key flows were validated functionally.

## Scalability
**Q:** What can be improved first for scaling?
**A:** Caching, async task queue for heavy operations, observability, and stronger role-based access controls.

## Deployment
**Q:** Is it deployable?
**A:** Yes. Config uses environment variables and `dj-database-url`, suitable for managed hosting setups.
