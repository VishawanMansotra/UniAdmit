"""
Management Command: seed_knowledge
Usage: python manage.py seed_knowledge

This command loads initial college knowledge into the database
so the chatbot can answer questions from day one.

To run: python manage.py seed_knowledge
"""

from django.core.management.base import BaseCommand
from chatbot.models import CollegeKnowledge


class Command(BaseCommand):
    help = 'Seeds initial college knowledge base for UniAdmit chatbot'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding college knowledge base...')

        knowledge_data = [

            # ── GENERAL INFO ──────────────────────────────────────────────
            {
                'category': 'general',
                'topic': 'About UIET',
                'information': (
                    'UIET (University Institute of Engineering & Technology) is a premier '
                    'engineering college under the University of Jammu, Jammu & Kashmir, India. '
                    'It offers undergraduate engineering programs with a focus on academic excellence '
                    'and holistic development.'
                ),
            },
            {
                'category': 'general',
                'topic': 'College Location',
                'information': (
                    'UIET is located in the University of Jammu campus, Jammu, Jammu & Kashmir. '
                    'It is easily accessible by road and is well-connected to the main city.'
                ),
            },
            {
                'category': 'contact',
                'topic': 'Contact Information',
                'information': (
                    'Admission Office: University of Jammu, Jammu – 180006.\n'
                    'Phone: Contact the university directly.\n'
                    'Website: www.uok.edu.in\n'
                    'Office Hours: Monday to Friday, 10:00 AM to 4:00 PM.'
                ),
            },

            # ── COURSES ───────────────────────────────────────────────────
            {
                'category': 'courses',
                'topic': 'B.Tech CSE (Computer Science Engineering)',
                'information': (
                    'Duration: 4 years (8 semesters).\n'
                    'Total Seats: 60 (approx).\n'
                    'Eligibility: 10+2 with Physics, Chemistry, Mathematics (PCM) with minimum 50% marks.\n'
                    'JEE Main score required.\n'
                    'Subjects include: Programming, Data Structures, DBMS, AI, Networks, Web Development, and more.\n'
                    'Degree awarded by University of Jammu.'
                ),
            },
            {
                'category': 'courses',
                'topic': 'B.Tech Civil Engineering',
                'information': (
                    'Duration: 4 years (8 semesters).\n'
                    'Total Seats: 60 (approx).\n'
                    'Eligibility: 10+2 with Physics, Chemistry, Mathematics (PCM) with minimum 50% marks.\n'
                    'JEE Main score required.\n'
                    'Subjects include: Structural Engineering, Fluid Mechanics, Construction, Surveying, and more.\n'
                    'Degree awarded by University of Jammu.'
                ),
            },

            # ── ADMISSIONS ────────────────────────────────────────────────
            {
                'category': 'admissions',
                'topic': 'Admission Process Overview',
                'information': (
                    'Step 1: Register on the UniAdmit portal.\n'
                    'Step 2: Fill the online application form with personal and academic details.\n'
                    'Step 3: Upload required documents (marksheets, certificates, photo, signature).\n'
                    'Step 4: Submit the application.\n'
                    'Step 5: Merit list will be published on the portal.\n'
                    'Step 6: Selected candidates attend document verification and counseling.\n'
                    'Step 7: Pay fees and confirm admission.'
                ),
            },
            {
                'category': 'admissions',
                'topic': 'Admission Timeline',
                'information': (
                    'Application Start: Check the official portal for dates.\n'
                    'Application Deadline: As notified on portal.\n'
                    'Merit List Publication: After deadline closes.\n'
                    'Document Verification: Announced after merit list.\n'
                    'Classes Begin: As per university academic calendar.\n'
                    'Note: All dates are subject to change. Check portal regularly.'
                ),
            },
            {
                'category': 'admissions',
                'topic': 'Merit List',
                'information': (
                    'Merit list is prepared based on JEE Main scores and 10+2 marks '
                    'as per the university merit formula.\n'
                    'Merit list is published on the UniAdmit portal.\n'
                    'Students can view their merit rank after login.\n'
                    'Category-wise merit lists are also published (General, SC, ST, OBC, etc.).'
                ),
            },
            {
                'category': 'admissions',
                'topic': 'How to Check Application Status',
                'information': (
                    'To check your application status:\n'
                    '1. Login to the UniAdmit portal.\n'
                    '2. Go to your Dashboard.\n'
                    '3. Click on "My Application".\n'
                    '4. Your current status will be displayed (Pending / Approved / Rejected).\n'
                    'If rejected, the reason/remarks will be shown.'
                ),
            },

            # ── ELIGIBILITY ───────────────────────────────────────────────
            {
                'category': 'eligibility',
                'topic': 'Eligibility for B.Tech Programs',
                'information': (
                    'Minimum Qualification: 10+2 or equivalent from a recognized board.\n'
                    'Required Subjects: Physics, Chemistry, and Mathematics (PCM).\n'
                    'Minimum Marks: 50% aggregate in PCM (45% for SC/ST candidates).\n'
                    'Entrance Exam: Valid JEE Main score is mandatory.\n'
                    'Age Limit: As per JEE Main norms (generally 17 years minimum).\n'
                    'Domicile: J&K domicile certificate may be required for state quota seats.'
                ),
            },
            {
                'category': 'eligibility',
                'topic': 'Required Documents for Admission',
                'information': (
                    '1. 10th Class Marksheet and Certificate.\n'
                    '2. 12th Class (10+2) Marksheet and Certificate.\n'
                    '3. JEE Main Scorecard.\n'
                    '4. Character Certificate from last institution.\n'
                    '5. Migration Certificate (if applicable).\n'
                    '6. Category Certificate (SC/ST/OBC) if applicable.\n'
                    '7. J&K Domicile Certificate.\n'
                    '8. Recent Passport-size Photographs (at least 6).\n'
                    '9. Aadhar Card / ID Proof.\n'
                    '10. Medical Fitness Certificate.'
                ),
            },

            # ── FEES ──────────────────────────────────────────────────────
            {
                'category': 'fees',
                'topic': 'Fee Structure',
                'information': (
                    'The exact fee structure is notified at the time of admission.\n'
                    'Fee categories include: Tuition Fee, Development Fee, Exam Fee, and other charges.\n'
                    'Fee concessions are available for SC/ST and economically weaker section students.\n'
                    'Scholarships like Reliance Foundation, J&K State Scholarship, and Post-Matric '
                    'Scholarship are available for eligible students.\n'
                    'For exact fee details, contact the admission office or check official notifications.'
                ),
            },

            # ── FACILITIES ────────────────────────────────────────────────
            {
                'category': 'facilities',
                'topic': 'Campus Facilities',
                'information': (
                    'UIET campus offers:\n'
                    '• Well-equipped computer labs with high-speed internet.\n'
                    '• Modern class rooms and seminar halls.\n'
                    '• Central library with large collection of books and journals.\n'
                    '• Sports facilities including outdoor courts.\n'
                    '• Canteen/cafeteria on campus.\n'
                    '• Wi-Fi enabled campus.\n'
                    '• Separate hostel facilities (boys and girls).\n'
                    '• Medical room for first aid.\n'
                    '• ATM facility nearby.'
                ),
            },
            {
                'category': 'hostel',
                'topic': 'Hostel Facilities',
                'information': (
                    'Hostel accommodation is available for both boys and girls on the University of Jammu campus.\n'
                    'Facilities include: Furnished rooms, common room, mess facility, Wi-Fi, and 24-hour security.\n'
                    'Hostel allotment is done on availability basis and merit.\n'
                    'For hostel enquiries, contact the University of Jammu hostel office directly.'
                ),
            },

            # ── PLACEMENT ─────────────────────────────────────────────────
            {
                'category': 'placement',
                'topic': 'Placement & Career',
                'information': (
                    'UIET has a Training & Placement cell that helps students with career guidance.\n'
                    'Companies from IT, construction, and government sectors visit for campus placements.\n'
                    'Students are encouraged to participate in internships, workshops, and hackathons.\n'
                    'Higher studies (M.Tech, MBA, M.Sc) are also pursued by many graduates.\n'
                    'Government job preparation (JKSSB, UPSC, SSC) support is also available.'
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
                    'Results are published on the University of Jammu official website.'
                ),
            },
        ]

        # Insert into database
        created_count = 0
        skipped_count = 0

        for entry in knowledge_data:
            obj, created = CollegeKnowledge.objects.get_or_create(
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
                skipped_count += 1
                self.stdout.write(f"  Skipped (exists): {entry['topic']}")

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created: {created_count}, Skipped: {skipped_count}'
        ))
        self.stdout.write(
            'Go to Django Admin -> College Knowledge to add/edit more entries.\n'
        )
