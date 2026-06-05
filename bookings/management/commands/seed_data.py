from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bookings.models import PoojaService, Pandit, Booking
from datetime import date, time, timedelta

class Command(BaseCommand):
    help = 'Seeds the database with users, certified Pandits, standard Pooja Services, and initial bookings.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting database seeding..."))

        # ----------------------------------------------------
        # 1. CREATE USERS
        # ----------------------------------------------------
        # Admin / Superuser
        admin_user, created = User.objects.get_or_create(username='admin')
        if created:
            admin_user.email = 'admin@devbhoomi.com'
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.first_name = 'DevBhoomi'
            admin_user.last_name = 'Admin'
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' created (PW: admin123)."))
        else:
            self.stdout.write("Superuser 'admin' already exists.")

        # Devotee / Customer
        customer_user, created = User.objects.get_or_create(username='durgesh')
        if created:
            customer_user.email = 'durgesh@gmail.com'
            customer_user.set_password('durgesh123')
            customer_user.first_name = 'Durgesh'
            customer_user.last_name = 'Rawat'
            customer_user.save()
            self.stdout.write(self.style.SUCCESS("Customer user 'durgesh' created (PW: durgesh123)."))
        else:
            self.stdout.write("Customer user 'durgesh' already exists.")

        # More customer users for dashboard metrics variation
        devotee_a, _ = User.objects.get_or_create(username='amit', defaults={
            'email': 'amit@gmail.com', 'first_name': 'Amit', 'last_name': 'Sharma'
        })
        devotee_a.set_password('customer123')
        devotee_a.save()

        devotee_b, _ = User.objects.get_or_create(username='sneha', defaults={
            'email': 'sneha@gmail.com', 'first_name': 'Sneha', 'last_name': 'Patil'
        })
        devotee_b.set_password('customer123')
        devotee_b.save()


        # ----------------------------------------------------
        # 2. CREATE POOJA SERVICES
        # ----------------------------------------------------
        services_data = [
            {
                'title': 'Ganesh Puja',
                'slug': 'ganesh-puja',
                'description': 'A holy ritual dedicated to Lord Ganesh, the remover of obstacles. Invokes positive energies, wisdom, and prosperity for any new venture, household harmony, or general well-being.',
                'estimated_duration_hours': 1.5,
                'base_price': 2100,
                'image': 'https://images.unsplash.com/photo-1562979314-dee785091f4d?auto=format&fit=crop&q=80&w=600'
            },
            {
                'title': 'Satyanarayan Puja',
                'slug': 'satyanarayan-puja',
                'description': 'A popular Vedic ritual devoted to Lord Vishnu in his Satyanarayan form. Usually conducted on Purnima (full moon days) to bring health, wealth, peace, and abundance to the household.',
                'estimated_duration_hours': 2.5,
                'base_price': 3100,
                'image': 'https://images.unsplash.com/photo-1602631985686-2bb0686a6a5a?auto=format&fit=crop&q=80&w=600'
            },
            {
                'title': 'Maha Mrityunjaya Jaap',
                'slug': 'maha-mrityunjaya-jaap',
                'description': 'A highly powerful Vedic chant dedicated to Lord Shiva to seek longevity, divine protection, and triumph over critical health conditions, negative forces, and cosmic blockages.',
                'estimated_duration_hours': 6.0,
                'base_price': 11000,
                'image': 'https://images.unsplash.com/photo-1609137144814-1e0e56011707?auto=format&fit=crop&q=80&w=600'
            },
            {
                'title': 'Griha Pravesh Puja',
                'slug': 'griha-pravesh-puja',
                'description': 'An essential housewarming ceremony performed before moving into a new home. Purifies the space from negative influences, bringing harmony, good fortune, and bliss to the family.',
                'estimated_duration_hours': 3.5,
                'base_price': 5100,
                'image': 'https://images.unsplash.com/photo-1609081219090-a6d81d3085bf?auto=format&fit=crop&q=80&w=600'
            },
            {
                'title': 'Rudrabhishek Puja',
                'slug': 'rudrabhishek-puja',
                'description': 'A sacred bathing ritual of the Shiva Lingam performed with milk, honey, curd, and holy water while chanting powerful mantras. Invokes Shiva\'s blessings for planetary corrections and spiritual peace.',
                'estimated_duration_hours': 2.0,
                'base_price': 4500,
                'image': 'https://images.unsplash.com/photo-1545128485-c400e7702796?auto=format&fit=crop&q=80&w=600'
            }
        ]

        services_instances = {}
        for s_info in services_data:
            service, created = PoojaService.objects.get_or_create(
                slug=s_info['slug'],
                defaults={
                    'title': s_info['title'],
                    'description': s_info['description'],
                    'estimated_duration_hours': s_info['estimated_duration_hours'],
                    'base_price': s_info['base_price'],
                    'image': s_info['image']
                }
            )
            services_instances[s_info['slug']] = service
            if created:
                self.stdout.write(self.style.SUCCESS(f"Pooja Service '{service.title}' created."))
            else:
                self.stdout.write(f"Pooja Service '{service.title}' already exists.")


        # ----------------------------------------------------
        # 3. CREATE PANDITS
        # ----------------------------------------------------
        pandit_data = [
            {
                'username': 'ramshastri',
                'first_name': 'Ram',
                'last_name': 'Shastri',
                'phone_number': '9876543210',
                'languages_spoken': 'Hindi, Sanskrit',
                'base_city': 'Varanasi',
                'profile_picture': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&q=80&w=150',
                'specializations': ['ganesh-puja', 'satyanarayan-puja', 'rudrabhishek-puja']
            },
            {
                'username': 'vishnuprasad',
                'first_name': 'Vishnu',
                'last_name': 'Prasad',
                'phone_number': '9876543211',
                'languages_spoken': 'Hindi, Sanskrit, Marathi',
                'base_city': 'Mumbai',
                'profile_picture': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&q=80&w=150',
                'specializations': ['satyanarayan-puja', 'griha-pravesh-puja']
            },
            {
                'username': 'ananddev',
                'first_name': 'Anand',
                'last_name': 'Dev',
                'phone_number': '9876543212',
                'languages_spoken': 'Hindi, Sanskrit',
                'base_city': 'Varanasi',
                'profile_picture': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=150',
                'specializations': ['maha-mrityunjaya-jaap', 'rudrabhishek-puja', 'ganesh-puja']
            }
        ]

        pandit_instances = {}
        for p_info in pandit_data:
            p_user, u_created = User.objects.get_or_create(username=p_info['username'], defaults={
                'email': f"{p_info['username']}@devbhoomi.com",
                'first_name': p_info['first_name'],
                'last_name': p_info['last_name']
            })
            p_user.set_password('pandit123')
            p_user.save()

            pandit, p_created = Pandit.objects.get_or_create(
                user=p_user,
                defaults={
                    'phone_number': p_info['phone_number'],
                    'profile_picture': p_info['profile_picture'],
                    'languages_spoken': p_info['languages_spoken'],
                    'base_city': p_info['base_city'],
                    'is_available': True
                }
            )
            # Link specializations
            for spec_slug in p_info['specializations']:
                if spec_slug in services_instances:
                    pandit.specialization.add(services_instances[spec_slug])
            
            pandit_instances[p_info['username']] = pandit
            if p_created:
                self.stdout.write(self.style.SUCCESS(f"Pandit '{pandit}' registered."))
            else:
                self.stdout.write(f"Pandit '{pandit}' already exists.")


        # ----------------------------------------------------
        # 4. CREATE SEED BOOKINGS
        # ----------------------------------------------------
        # We delete existing bookings so the metrics match perfectly with our seed scenario on clean runs
        Booking.objects.all().delete()

        today = date.today()

        # Booking 1: CONFIRMED - Durgesh Ganesh Puja, assigned to Ram Shastri
        Booking.objects.create(
            customer=customer_user,
            pooja=services_instances['ganesh-puja'],
            assigned_pandit=pandit_instances['ramshastri'],
            date_of_pooja=today + timedelta(days=5),
            muhurat_time=time(9, 30),
            venue_address="Apt 402, Shiv Shanti Residency, Sigra, Varanasi, UP - 221010",
            status='CONFIRMED'
        )

        # Booking 2: PENDING - Durgesh Satyanarayan Puja, Unassigned
        Booking.objects.create(
            customer=customer_user,
            pooja=services_instances['satyanarayan-puja'],
            assigned_pandit=None,
            date_of_pooja=today + timedelta(days=7),
            muhurat_time=time(17, 15),
            venue_address="Apt 402, Shiv Shanti Residency, Sigra, Varanasi, UP - 221010",
            status='PENDING'
        )

        # Booking 3: COMPLETED - Amit Rudrabhishek Puja, assigned to Anand Dev (past booking)
        Booking.objects.create(
            customer=devotee_a,
            pooja=services_instances['rudrabhishek-puja'],
            assigned_pandit=pandit_instances['ananddev'],
            date_of_pooja=today - timedelta(days=8),
            muhurat_time=time(7, 00),
            venue_address="Ghat House #14, Dashashwamedh Ghat, Varanasi, UP - 221001",
            status='COMPLETED'
        )

        # Booking 4: PENDING - Sneha Maha Mrityunjaya, Unassigned
        Booking.objects.create(
            customer=devotee_b,
            pooja=services_instances['maha-mrityunjaya-jaap'],
            assigned_pandit=None,
            date_of_pooja=today + timedelta(days=12),
            muhurat_time=time(6, 30),
            venue_address="Flat 1002, B-Wing, Omkar Tower, Andheri East, Mumbai, MH - 400069",
            status='PENDING'
        )

        # Booking 5: CONFIRMED - Sneha Griha Pravesh, assigned to Vishnu Prasad
        Booking.objects.create(
            customer=devotee_b,
            pooja=services_instances['griha-pravesh-puja'],
            assigned_pandit=pandit_instances['vishnuprasad'],
            date_of_pooja=today + timedelta(days=2),
            muhurat_time=time(11, 00),
            venue_address="Flat 1002, B-Wing, Omkar Tower, Andheri East, Mumbai, MH - 400069",
            status='CONFIRMED'
        )

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
