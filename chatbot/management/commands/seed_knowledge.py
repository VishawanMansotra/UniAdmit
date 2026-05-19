"""
Management Command: seed_knowledge
Usage: python manage.py seed_knowledge

This command loads initial college knowledge into the database
so the chatbot can answer questions from day one.

Updated with official UIET Admission Notification 2026-27
(Ref: No.UIET/KC/JU/2026-27/126 dated 05-05-2026)

To run: python manage.py seed_knowledge
"""

from django.core.management.base import BaseCommand
from chatbot.models import CollegeKnowledge


class Command(BaseCommand):
    help = 'Seeds initial college knowledge base for UniAdmit chatbot (2026-27 updated)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding college knowledge base...')

        knowledge_data = [

            # ── GENERAL INFO ──────────────────────────────────────────────
            {
                'category': 'general',
                'topic': 'About UIET',
                'information': (
                    'UIET (University Institute of Engineering & Technology) Kathua Campus is a premier '
                    'engineering college under the University of Jammu, Jammu & Kashmir, India. '
                    'It is located at Kathua Campus, University of Jammu. '
                    'The college motto is: "Through study and teaching, one attains the nectar of knowledge." '
                    'It offers B.Tech undergraduate programs in CSE, Civil Engineering, and ECE '
                    'with a focus on academic excellence and holistic development. '
                    'Total intake: 180 seats (60 per program).'
                ),
            },
            {
                'category': 'general',
                'topic': 'College Location',
                'information': (
                    'UIET is located at Kathua Campus, University of Jammu, Kathua, Jammu & Kashmir. '
                    'Phone: 01922-297470. '
                    'Email: uietkc@jammuuniversity.ac.in. '
                    'It is easily accessible by road and well-connected to Kathua city.'
                ),
            },
            {
                'category': 'contact',
                'topic': 'Contact Information',
                'information': (
                    'Admission Office: UIET, Kathua Campus, University of Jammu, Kathua – J&K.\n'
                    'Phone: 01922-297470.\n'
                    'Email: uietkc@jammuuniversity.ac.in.\n'
                    'Web Master: itcell.uietju@gmail.com.\n'
                    'Office Hours: Monday to Friday, 10:00 AM to 4:00 PM.\n'
                    'For admissions specifically, email: uietkc@jammuuniversity.ac.in.'
                ),
            },

            # ── COURSES ───────────────────────────────────────────────────
            {
                'category': 'courses',
                'topic': 'B.Tech CSE (Computer Science Engineering)',
                'information': (
                    'Program: B.Tech Computer Science Engineering (CSE).\n'
                    'Duration: 4 years (8 semesters).\n'
                    'Total Seats: 60 (2026-27).\n'
                    'Seat Split: 48 seats for JU jurisdiction students (80%), 12 seats open (20%).\n'
                    'Eligibility: 10+2 with Physics, Chemistry, Mathematics (PCM).\n'
                    'Entrance: Valid JEE Mains 2026 score required for Round 1.\n'
                    'Subjects include: Programming, Data Structures, DBMS, AI, Networks, Web Development, and more.\n'
                    'Degree awarded by University of Jammu.'
                ),
            },
            {
                'category': 'courses',
                'topic': 'B.Tech Civil Engineering',
                'information': (
                    'Program: B.Tech Civil Engineering.\n'
                    'Duration: 4 years (8 semesters).\n'
                    'Total Seats: 60 (2026-27).\n'
                    'Seat Split: 48 seats for JU jurisdiction students (80%), 12 seats open (20%).\n'
                    'Eligibility: 10+2 with Physics, Chemistry, Mathematics (PCM).\n'
                    'Entrance: Valid JEE Mains 2026 score required for Round 1.\n'
                    'Subjects include: Structural Engineering, Fluid Mechanics, Construction, Surveying, and more.\n'
                    'Degree awarded by University of Jammu.'
                ),
            },
            {
                'category': 'courses',
                'topic': 'B.Tech ECE (Electronics and Communication Engineering)',
                'information': (
                    'Program: B.Tech Electronics and Communication Engineering (ECE).\n'
                    'Duration: 4 years (8 semesters).\n'
                    'Total Seats: 60 (2026-27).\n'
                    'Seat Split: 48 seats for JU jurisdiction students (80%), 12 seats open (20%).\n'
                    'Eligibility: 10+2 with Physics, Chemistry, Mathematics (PCM).\n'
                    'Entrance: Valid JEE Mains 2026 score required for Round 1.\n'
                    'Subjects include: Electronics, Communication Systems, Signal Processing, VLSI, Embedded Systems, and more.\n'
                    'Degree awarded by University of Jammu.'
                ),
            },

            # ── ADMISSIONS ────────────────────────────────────────────────
            {
                'category': 'admissions',
                'topic': 'Admission Process Overview',
                'information': (
                    'Step 1: Register on the UniAdmit portal (this website).\n'
                    'Step 2: Verify your email via OTP.\n'
                    'Step 3: Fill the online application form with personal and academic details.\n'
                    'Step 4: Upload required documents (marksheets, certificates, photo, signature).\n'
                    'Step 5: Pay the application fee of Rs. 1,500/- via J&K Bank.\n'
                    'Step 6: Submit the application — no changes allowed after submission.\n'
                    'Step 7: Merit list will be published on 02 June 2026.\n'
                    'Step 8: Selected candidates attend document verification and counseling.\n'
                    'Step 9: Pay semester fees and confirm admission.'
                ),
            },
            {
                'category': 'admissions',
                'topic': 'Admission Timeline 2026-27',
                'information': (
                    'Official Admission Dates for 2026-27 (Ref: No.UIET/KC/JU/2026-27/126):\n'
                    '• Applications Open: 11 May 2026.\n'
                    '• Last Date without late fee: 24 May 2026.\n'
                    '• Last Date with Rs. 110 late fee: 31 May 2026.\n'
                    '• Selection List Published: 02 June 2026.\n'
                    'Note: All dates are as per the official notification. Check the portal for updates.'
                ),
            },
            {
                'category': 'admissions',
                'topic': 'Admission Rounds — JEE, CUET, 10+2',
                'information': (
                    'Admissions at UIET 2026-27 are conducted in up to 3 rounds:\n\n'
                    'Round 1 — JEE Mains 2026 (Primary Round):\n'
                    '  Admission is based on JEE Mains 2026 score merit. This is the main round.\n\n'
                    'Round 2 — CUET UG (If seats remain after Round 1):\n'
                    '  Admission based on CUET UG score. A separate notification will be issued.\n\n'
                    'Round 3 — 10+2 / Higher Secondary Score (If seats still remain after Round 2):\n'
                    '  Admission based on Class 12 board examination marks. A separate notification will be issued.\n\n'
                    'Note: Seats will be allotted strictly on merit and branch preference.'
                ),
            },
            {
                'category': 'admissions',
                'topic': 'Seat Distribution and Reservation',
                'information': (
                    'Total Seats: 180 (60 per program × 3 programs).\n'
                    'Seat Distribution per program (60 seats):\n'
                    '  • 80% = 48 seats for students from schools under University of Jammu jurisdiction.\n'
                    '  • 20% = 12 seats open to all students from rest of UT/Country.\n'
                    'Programs: B.Tech CSE, B.Tech Civil Engineering, B.Tech ECE.\n'
                    'Within each category, further reservation as per Govt. of J&K norms applies.'
                ),
            },
            {
                'category': 'admissions',
                'topic': 'Merit List',
                'information': (
                    'Merit list for 2026-27 will be published on 02 June 2026 on the UniAdmit portal.\n'
                    'Round 1 merit is based on JEE Mains 2026 score.\n'
                    'If Round 2 (CUET) or Round 3 (10+2) are needed, separate merit lists will be published.\n'
                    'Category-wise merit lists are prepared (General, SC, ST, OBC, EWS, PWD).\n'
                    'Students can view their application status after login to the portal.'
                ),
            },
            {
                'category': 'admissions',
                'topic': 'How to Check Application Status',
                'information': (
                    'To check your application status:\n'
                    '1. Login to the UniAdmit portal.\n'
                    '2. Go to your Dashboard.\n'
                    '3. Click on "My Applications".\n'
                    '4. Your current status will be displayed (Pending / Approved / Rejected).\n'
                    'If rejected, remarks will be shown. For queries, email: uietkc@jammuuniversity.ac.in.'
                ),
            },
            {
                'category': 'admissions',
                'topic': 'Important Instructions for Applicants',
                'information': (
                    'Official instructions from UIET Admission Notice 2026-27:\n'
                    '1. Read all instructions carefully before filling the application form.\n'
                    '2. Fill the form properly and accurately.\n'
                    '3. Changes are NOT allowed once the application form is submitted.\n'
                    '4. Provide a working Email ID and Contact Number.\n'
                    '5. Application fee is Rs. 1,500/- (without late fee).\n'
                    '6. Upload all required documents.\n'
                    '7. An acknowledgement will be sent after successful submission.\n'
                    '8. Submission of application does NOT guarantee admission.\n'
                    '9. Seats are allotted strictly on merit and branch preference.'
                ),
            },

            # ── ELIGIBILITY ───────────────────────────────────────────────
            {
                'category': 'eligibility',
                'topic': 'Eligibility for B.Tech Programs',
                'information': (
                    'Minimum Qualification: 10+2 or equivalent from a recognized board.\n'
                    'Required Subjects: Physics, Chemistry, and Mathematics (PCM).\n'
                    'Entrance Exam (Round 1): Valid JEE Mains 2026 score is mandatory.\n'
                    'Round 2 (if applicable): Valid CUET UG score.\n'
                    'Round 3 (if applicable): 10+2 / Higher Secondary marks.\n'
                    'Domicile: J&K Domicile Certificate required.\n'
                    'Category Certificate required for SC/ST/OBC/EWS/PWD candidates.'
                ),
            },
            {
                'category': 'eligibility',
                'topic': 'Required Documents for Application',
                'information': (
                    'Documents required at the time of applying (2026-27):\n'
                    '1. 10th Class Marksheet.\n'
                    '2. 12th Class (10+2) Marksheet.\n'
                    '3. JEE Mains 2026 Score Card (mandatory for Round 1).\n'
                    '4. Date of Birth Certificate.\n'
                    '5. Domicile Certificate (J&K).\n'
                    '6. Category Certificate (SC/ST/OBC/EWS/PWD) — if applicable.\n'
                    '7. Proof of Fee Payment (Bank receipt of Rs. 1,500/-).\n'
                    '8. Passport-size Photograph and Signature.\n\n'
                    'Additional documents required for shortlisted candidates at the time of counseling:\n'
                    '- Achievement Category Documents (if applicable).\n'
                    '- Medical Fitness Certificate.\n'
                    '- Migration Certificate (if applicable).'
                ),
            },

            # ── FEES ──────────────────────────────────────────────────────
            {
                'category': 'fees',
                'topic': 'Application Fee 2026-27',
                'information': (
                    'Application Fee for UIET Admission 2026-27:\n'
                    '• Without late fee: Rs. 1,500/- (deadline: 24 May 2026).\n'
                    '• With late fee: Rs. 1,610/- (Rs. 1,500 + Rs. 110 late fee, deadline: 31 May 2026).\n\n'
                    'Payment Method: Bank Transfer (NEFT/RTGS/IMPS).\n'
                    'Bank: J&K Bank Ltd., Patel Nagar, Kathua.\n'
                    'Account Number: 0345040500000175.\n'
                    'IFSC Code: JAKA0REVENU.\n'
                    'Account Holder: Co-ordinator UIET, University of Jammu.\n\n'
                    'Keep the payment receipt/transaction proof as it must be uploaded with the application.'
                ),
            },
            {
                'category': 'fees',
                'topic': 'Bank Details for Fee Payment',
                'information': (
                    'To pay the UIET 2026-27 application fee, use the following bank details:\n'
                    'Account Holder: Co-ordinator UIET, University of Jammu.\n'
                    'Bank: J&K Bank Ltd.\n'
                    'Branch: Patel Nagar, Kathua.\n'
                    'Account Number: 0345040500000175.\n'
                    'IFSC Code: JAKA0REVENU.\n'
                    'Amount: Rs. 1,500/- (before 24 May 2026) or Rs. 1,610/- (before 31 May 2026).\n'
                    'After payment, keep the transaction receipt and upload it in the application form.'
                ),
            },

            # ── FACILITIES ────────────────────────────────────────────────
            {
                'category': 'facilities',
                'topic': 'Campus Facilities',
                'information': (
                    'UIET Kathua Campus offers:\n'
                    '• Well-equipped computer labs with high-speed internet.\n'
                    '• Modern classrooms and seminar halls.\n'
                    '• Central library with books, journals, and eLibrary access.\n'
                    '• Sports facilities including outdoor courts.\n'
                    '• Canteen/cafeteria on campus.\n'
                    '• Wi-Fi enabled campus.\n'
                    '• Girls hostel (inaugurated and operational).\n'
                    '• 3D Printing facility (installed 2025).\n'
                    '• NCC unit on campus.\n'
                    '• Science Club, Community Service Club, and more.'
                ),
            },
            {
                'category': 'hostel',
                'topic': 'Hostel Facilities',
                'information': (
                    'Girls Hostel is available on the UIET Kathua Campus (inaugurated in 2024).\n'
                    'Facilities include: Furnished rooms, mess facility, Wi-Fi, and security.\n'
                    'For hostel enquiries, contact the UIET Kathua Campus directly.\n'
                    'Phone: 01922-297470. Email: uietkc@jammuuniversity.ac.in.'
                ),
            },

            # ── PLACEMENT ─────────────────────────────────────────────────
            {
                'category': 'placement',
                'topic': 'Placement & Career',
                'information': (
                    'UIET Kathua Campus has a Training & Placement cell.\n'
                    'Students have secured internships in top IT and Civil Engineering organizations.\n'
                    'Students are encouraged to participate in internships, workshops, and hackathons.\n'
                    'National-level programs: AICTE internship portal (internship.aicte-india.org) and AICTE career portal.\n'
                    'Students have won medals in Inter-College Boxing and other sports championships.\n'
                    'Higher studies (M.Tech, MBA) and government jobs (JKSSB, UPSC) are common career paths.'
                ),
            },

            # ── EXAMS ─────────────────────────────────────────────────────
            {
                'category': 'exam',
                'topic': 'Examination Pattern',
                'information': (
                    'University of Jammu conducts semester-wise examinations.\n'
                    'Each semester has: Internal Assessment (30 marks) + End Semester Exam (70 marks).\n'
                    'Minimum passing marks: 40% in each subject.\n'
                    'Students must maintain 75% attendance to appear in examinations.\n'
                    'Results are published on the University of Jammu official website.\n'
                    'Time tables are published on the UIET website (uiet.kathuacampus.in).'
                ),
            },
        ]

        # Insert or UPDATE into database (update_or_create ensures existing entries get refreshed)
        created_count = 0
        updated_count = 0

        for entry in knowledge_data:
            obj, created = CollegeKnowledge.objects.update_or_create(
                topic=entry['topic'],
                defaults={
                    'category': entry['category'],
                    'information': entry['information'],
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"  Added: {entry['topic']}")
            else:
                updated_count += 1
                self.stdout.write(f"  Updated: {entry['topic']}")

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created: {created_count}, Updated: {updated_count}'
        ))
        self.stdout.write(
            'Go to Django Admin -> College Knowledge to add/edit more entries.\n'
        )
