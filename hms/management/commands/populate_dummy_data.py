import random
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from hms.models import Student, Payment, MaintenanceRequest, Visitor, DefermentRequest, Meal
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Populates the database with dummy data for analytics trends'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating dummy data...')

        try:
            # 1. Ensure we have some students
            students = self.get_or_create_students(count=10)
            self.stdout.write(f'Using {len(students)} students.')
            
            if not students:
                self.stdout.write(self.style.ERROR('No students found or created. Aborting.'))
                return

            # 2. Generate data for the past 30 days AND future 7 days (to cover the full current week)
            today = timezone.now()
            # Ensure we cover the LAST WEEK (Mon-Sun) heavily to show trends
            current_week_start = today - timedelta(days=today.weekday())
            start_date = current_week_start - timedelta(days=7) # Start from last week
            end_date = current_week_start + timedelta(days=6) # End this Sunday
            
            current_date = start_date
            while current_date <= end_date:
                # self.stdout.write(f'Generating data for {current_date.date()}...')
                
                # Payments
                if random.random() > 0.3: # 70% chance of payments
                    num = random.randint(1, 4)
                    for _ in range(num):
                        self.create_payment(random.choice(students), current_date)

                # Maintenance
                if random.random() > 0.5: # 50% chance
                    num = random.randint(1, 3)
                    for _ in range(num):
                        self.create_maintenance(random.choice(students), current_date)

                # Visitors
                if random.random() > 0.2: # 80% chance
                    num = random.randint(2, 6)
                    for _ in range(num):
                        self.create_visitor(random.choice(students), current_date)

                # Deferments (Boost chance for visibility)
                if random.random() > 0.5: # 50% chance (increased from 20%)
                    num = random.randint(1, 3) # 1-3 requests
                    for _ in range(num):
                        self.create_deferment(random.choice(students), current_date)
                
                # Meals (Daily for most students)
                self.create_meals(students, current_date)

                current_date += timedelta(days=1)

            self.stdout.write(self.style.SUCCESS('Successfully populated dummy data (targeted for current week)!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Critical error: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())

    def get_or_create_students(self, count=10):
        students = list(Student.objects.all())
        if len(students) >= count:
            return students[:count]
        
        needed = count - len(students)
        created = 0
        attempts = 0
        
        while created < needed and attempts < 50:
            attempts += 1
            try:
                username = f'dummy_student_{random.randint(10000, 99999)}'
                if User.objects.filter(username=username).exists():
                    continue
                    
                user = User.objects.create_user(username=username, password='password123')
                user.first_name = 'Student'
                user.last_name = f'Dummy{random.randint(100,999)}'
                user.save()
                
                student = Student.objects.create(
                    user=user,
                    university_id=f'DUMMY{random.randint(10000, 99999)}',
                    phone=f'07{random.randint(10000000, 99999999)}',
                    residence_type='hostel'
                )
                students.append(student)
                created += 1
            except Exception as e:
                self.stdout.write(f"Error creating student: {e}")
                
        return students

    def create_payment(self, student, date_obj):
        try:
            p = Payment.objects.create(
                student=student,
                amount=random.choice([1000, 2000, 500, 15000]),
                phone_number=student.phone,
                transaction_id=f'TRX{random.randint(100000,999999)}{random.randint(10,99)}',
                status='Completed'
            )
            # Force update created_at
            Payment.objects.filter(pk=p.pk).update(created_at=date_obj)
        except Exception as e:
             # self.stdout.write(f"Error creating payment: {e}")
             pass

    def create_maintenance(self, student, date_obj):
        try:
            m = MaintenanceRequest.objects.create(
                student=student,
                title=random.choice(['Broken Socket', 'Leaking Tap', 'Light Bulb', 'Door Lock']),
                description='Fix it please',
                priority=random.choice(['low', 'medium', 'high']),
                status=random.choice(['pending', 'in_progress', 'completed'])
            )
            # Force update created_at
            MaintenanceRequest.objects.filter(pk=m.pk).update(created_at=date_obj)
        except Exception as e:
             # self.stdout.write(f"Error creating maintenance: {e}")
             pass

    def create_visitor(self, student, date_obj):
        try:
            v = Visitor.objects.create(
                student=student,
                name=f'Visitor {random.randint(1,100)}',
                category=random.choice(['male_student', 'female_student', 'male_parent']),
                purpose='Visit',
                is_active=False
            )
            # Force update check_in_time and check_out_time
            Visitor.objects.filter(pk=v.pk).update(
                check_in_time=date_obj,
                check_out_time=date_obj + timedelta(hours=2)
            )
        except Exception as e:
             # self.stdout.write(f"Error creating visitor: {e}")
             pass

    def create_deferment(self, student, date_obj):
        try:
            d = DefermentRequest.objects.create(
                student=student,
                start_date=date_obj.date(),
                end_date=date_obj.date() + timedelta(days=7),
                deferment_type=random.choice(['sick_role', 'fee_challenges']),
                reason='Dummy reason',
                status=random.choice(['pending', 'approved'])
            )
            # Force update created_at
            DefermentRequest.objects.filter(pk=d.pk).update(created_at=date_obj)
        except Exception as e:
             # self.stdout.write(f"Error creating deferment: {e}")
             pass

    def create_meals(self, students, date_obj):
        # 60% take both, 20% breakfast only, 10% supper only, 10% away
        for student in students:
            # Check if meal already exists
            if Meal.objects.filter(student=student, date=date_obj.date()).exists():
                continue

            try:
                roll = random.random()
                breakfast = False
                supper = False
                away = False

                if roll < 0.6:
                    breakfast = True
                    supper = True
                elif roll < 0.8:
                    breakfast = True
                elif roll < 0.9:
                    supper = True
                else:
                    away = True
                
                Meal.objects.create(
                    student=student,
                    date=date_obj.date(),
                    breakfast=breakfast,
                    supper=supper,
                    away=away
                )
            except Exception as e:
                 # self.stdout.write(f"Error creating meal: {e}")
                 pass
