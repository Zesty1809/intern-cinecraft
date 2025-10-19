import random
from datetime import date, timedelta

from cineapp.models import DepartmentProfile
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create sample DepartmentProfile entries for testing submissions page.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of fake profiles to generate (default: 20)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing profiles before generating new ones'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        if options['clear']:
            deleted_count = DepartmentProfile.objects.all().count()
            DepartmentProfile.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted_count} existing profiles.'))
        
        # Sample data pools
        first_names = [
            'Rajesh', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Anjali', 'Arjun', 'Deepika',
            'Karan', 'Pooja', 'Rahul', 'Neha', 'Sanjay', 'Divya', 'Ravi', 'Kavya',
            'Aditya', 'Shreya', 'Rohan', 'Meera', 'Nikhil', 'Isha', 'Vivek', 'Ananya',
            'Suresh', 'Lakshmi', 'Manoj', 'Swati', 'Harish', 'Nisha', 'Prakash', 'Ritu'
        ]
        
        last_names = [
            'Kumar', 'Sharma', 'Patel', 'Singh', 'Reddy', 'Gupta', 'Rao', 'Nair',
            'Iyer', 'Menon', 'Chopra', 'Verma', 'Das', 'Kapoor', 'Malhotra', 'Bose',
            'Mehta', 'Joshi', 'Desai', 'Shah', 'Pillai', 'Agarwal', 'Mishra', 'Pandey'
        ]
        
        departments = [
            'Direction Department', 'Cinematography', 'Music Department', 
            'Sound Department', 'Editing Department', 'Art Department',
            'Costume Design', 'Make Up Department', 'Visual Effects',
            'Production Department', 'Lighting Department', 'Camera Department',
            'Choreography', 'Casting Department', 'Script Department'
        ]
        
        cities = [
            'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata',
            'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow', 'Kochi', 'Chandigarh'
        ]
        
        states = [
            'Maharashtra', 'Delhi', 'Karnataka', 'Telangana', 'Tamil Nadu', 'West Bengal',
            'Maharashtra', 'Gujarat', 'Rajasthan', 'Uttar Pradesh', 'Kerala', 'Punjab'
        ]
        
        skills_pool = [
            ['Direction', 'Screenwriting', 'Story Development', 'Creative Vision'],
            ['Camera Operation', 'Lighting', 'Framing', 'Visual Storytelling'],
            ['Music Composition', 'Sound Design', 'Mixing', 'Audio Engineering'],
            ['Video Editing', 'Color Grading', 'Post Production', 'Adobe Premiere'],
            ['Set Design', 'Props Management', 'Production Design', 'Art Direction'],
            ['Costume Design', 'Wardrobe Management', 'Period Costumes', 'Fashion'],
            ['Special Effects Makeup', 'Prosthetics', 'Character Design', 'Beauty Makeup'],
            ['3D Modeling', 'CGI', 'Motion Graphics', 'Compositing'],
            ['Production Management', 'Scheduling', 'Budget Planning', 'Team Coordination'],
            ['Lighting Setup', 'Gaffer Work', 'Electrical', 'Grip Work'],
        ]
        
        projects_pool = [
            'Worked on major Telugu film with leading actors',
            'Contributed to award-winning Hindi web series',
            'Assisted in production of Tamil blockbuster',
            'Part of team for Malayalam critically acclaimed film',
            'Worked on multiple advertisements and music videos',
            'Freelance work on various independent projects',
            'Collaborated with renowned director on feature film',
            'Portfolio includes commercial ads and short films',
            'Experience in both regional and national projects',
            'Worked on Netflix original series',
        ]
        
        availability_options = [
            'Immediately Available', 'Available in 2 weeks', 'Available from next month',
            'Currently on project, available in 1 month', 'Flexible availability'
        ]
        
        approval_statuses = ['pending', 'approved', 'rejected', 'inactive']
        status_weights = [0.4, 0.3, 0.15, 0.15]  # More pending and approved
        
        created_count = 0
        
        for i in range(count):
            full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            department = random.choice(departments)
            city = random.choice(cities)
            state = states[cities.index(city)]
            
            # Generate realistic data
            years_exp = random.randint(1, 20)
            age = random.randint(25, 55)
            dob = date.today() - timedelta(days=age*365 + random.randint(0, 365))
            
            profile_data = {
                'full_name': full_name,
                'email': f"{full_name.lower().replace(' ', '.')}@example.com",
                'phone_number': f"+91 {random.randint(7000000000, 9999999999)}",
                'department_name': department,
                'date_of_birth': dob,
                'address': f"{random.randint(1, 999)} {random.choice(['MG Road', 'Park Street', 'Main Street', 'Film Nagar', 'Jubilee Hills', 'Banjara Hills', 'Anna Nagar', 'T Nagar'])}",
                'city': city,
                'state': state,
                'pin_code': f"{random.randint(100000, 999999)}",
                'years_of_experience': years_exp,
                'key_skills': ', '.join(random.choice(skills_pool)),
                'previous_projects': random.choice(projects_pool),
                'availability': random.choice(availability_options),
                'expected_salary_range': f"₹{random.randint(30, 150)}K - ₹{random.randint(151, 300)}K per project",
                'performed_work_location': f"{city}, {random.choice([c for c in cities if c != city])}",
                'educational_qualification': random.choice([
                    'Bachelor of Fine Arts in Film Making',
                    'Diploma in Cinematography',
                    'Master of Arts in Music',
                    'Bachelor of Technology',
                    'Diploma in Film Technology',
                    'Self-taught with practical experience',
                    'Film School Graduate',
                    'Bachelor of Arts in Theatre'
                ]),
                'certifications_training': random.choice([
                    'FTII Certificate in Cinematography',
                    'Advanced editing course from Editing Institute',
                    'Sound Design Workshop by Industry Expert',
                    'Online courses in Visual Effects',
                    'Direction Workshop by Renowned Director',
                    '',
                ]),
                'awards_recognition': random.choice([
                    'Best Cinematography Award at Regional Film Festival',
                    'Nominated for Best Editing at Film Awards',
                    'Recognition for Outstanding Contribution',
                    'Winner of Best Debut Award',
                    '',
                    '',
                ]),
                'portfolio_link': f"https://portfolio.{full_name.lower().replace(' ', '')}.com" if random.random() > 0.3 else '',
                'linkedin_profile': f"https://linkedin.com/in/{full_name.lower().replace(' ', '-')}" if random.random() > 0.2 else '',
                'imdb_profile': f"https://imdb.com/name/nm{random.randint(1000000, 9999999)}" if random.random() > 0.5 else '',
                'additional_information': random.choice([
                    'Passionate about creating visually stunning content',
                    'Strong team player with excellent communication skills',
                    'Committed to delivering high-quality work on time',
                    'Open to learning new techniques and technologies',
                    'Flexible and adaptable to project requirements',
                    '',
                ]),
                'approval_status': random.choices(approval_statuses, weights=status_weights)[0],
            }
            
            try:
                profile = DepartmentProfile.objects.create(**profile_data)
                created_count += 1
                status_color = {
                    'pending': self.style.WARNING,
                    'approved': self.style.SUCCESS,
                    'rejected': self.style.ERROR,
                    'inactive': self.style.MIGRATE_LABEL,
                }[profile.approval_status]
                
                self.stdout.write(
                    f"Created: {profile.full_name} - {profile.department_name} - "
                    f"{status_color(profile.approval_status.upper())} "
                    f"(ID: {profile.application_id})"
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create profile: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {created_count} sample profiles!'))
        self.stdout.write(self.style.SUCCESS(f'   - Pending: {DepartmentProfile.objects.filter(approval_status="pending").count()}'))
        self.stdout.write(self.style.SUCCESS(f'   - Approved: {DepartmentProfile.objects.filter(approval_status="approved").count()}'))
        self.stdout.write(self.style.SUCCESS(f'   - Rejected: {DepartmentProfile.objects.filter(approval_status="rejected").count()}'))
        self.stdout.write(self.style.SUCCESS(f'   - Inactive: {DepartmentProfile.objects.filter(approval_status="inactive").count()}'))
