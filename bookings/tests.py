from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from bookings.models import PoojaService, Pandit, Booking
from datetime import date, time, timedelta

class DevBhoomiPlatformTests(TestCase):
    def setUp(self):
        # 1. Create standard Pooja Services
        self.ganesh_puja = PoojaService.objects.create(
            title='Ganesh Puja',
            slug='ganesh-puja',
            description='Ganesh Puja Description',
            estimated_duration_hours=1.5,
            base_price=2100
        )
        self.satyanarayan_puja = PoojaService.objects.create(
            title='Satyanarayan Puja',
            slug='satyanarayan-puja',
            description='Satyanarayan Description',
            estimated_duration_hours=2.5,
            base_price=3100
        )

        # 2. Create Users
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@devbhoomi.com', password='admin123', is_staff=True
        )
        self.customer_user = User.objects.create_user(
            username='durgesh', email='durgesh@gmail.com', password='durgesh123'
        )

        # 3. Create Pandits
        self.pandit_user_1 = User.objects.create_user(
            username='ramshastri', email='ram@devbhoomi.com', password='pandit123', first_name='Ram', last_name='Shastri'
        )
        self.pandit_1 = Pandit.objects.create(
            user=self.pandit_user_1,
            phone_number='9876543210',
            languages_spoken='Hindi, Sanskrit',
            base_city='Varanasi',
            is_available=True
        )
        self.pandit_1.specialization.add(self.ganesh_puja)

        self.pandit_user_2 = User.objects.create_user(
            username='vishnuprasad', email='vishnu@devbhoomi.com', password='pandit123', first_name='Vishnu', last_name='Prasad'
        )
        self.pandit_2 = Pandit.objects.create(
            user=self.pandit_user_2,
            phone_number='9876543211',
            languages_spoken='Hindi, Marathi',
            base_city='Mumbai',
            is_available=True
        )
        self.pandit_2.specialization.add(self.satyanarayan_puja)

        # Initial Client
        self.client = Client()

    def test_pooja_service_model(self):
        """Test model creation and string representation of PoojaService."""
        self.assertEqual(str(self.ganesh_puja), 'Ganesh Puja')
        self.assertEqual(self.ganesh_puja.base_price, 2100)

    def test_pandit_model(self):
        """Test model creation and string representation of Pandit."""
        self.assertEqual(str(self.pandit_1), 'Pandit Ram Shastri (Varanasi)')
        self.assertEqual(self.pandit_1.base_city, 'Varanasi')

    def test_catalog_view(self):
        """Verify the grid catalog page loads successfully and filters correctly."""
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ganesh Puja')
        self.assertContains(response, 'Satyanarayan Puja')

        # Test search filter query
        response_search = self.client.get(reverse('catalog'), {'q': 'Ganesh'})
        self.assertEqual(response_search.status_code, 200)
        self.assertContains(response_search, 'Ganesh Puja')
        self.assertNotContains(response_search, 'Satyanarayan Puja')

    def test_detail_view(self):
        """Verify Pooja Service Detail page loads successfully."""
        response = self.client.get(reverse('detail', args=[self.ganesh_puja.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ganesh Puja Description')
        self.assertContains(response, '₹2100')

    def test_booking_checkout_flow_requires_auth(self):
        """Verify unauthenticated booking redirects to login."""
        response = self.client.get(reverse('book', args=[self.ganesh_puja.slug]))
        self.assertRedirects(response, f"/accounts/login/?next=/book/{self.ganesh_puja.slug}/")

    def test_booking_creation_and_history(self):
        """Verify successful booking creation creates database records in PENDING status."""
        self.client.login(username='durgesh', password='durgesh123')
        
        post_data = {
            'date_of_pooja': str(date.today() + timedelta(days=5)),
            'muhurat_time': '09:30',
            'venue_address': 'Apt 402, Shiv Residency, Sigra, Varanasi'
        }
        response = self.client.post(reverse('book', args=[self.ganesh_puja.slug]), data=post_data)
        
        # Check redirection to profile page
        self.assertRedirects(response, reverse('profile'))

        # Verify Booking was created in 'PENDING' status
        booking = Booking.objects.get(customer=self.customer_user)
        self.assertEqual(booking.pooja, self.ganesh_puja)
        self.assertEqual(booking.status, 'PENDING')
        self.assertNil = self.assertIsNone(booking.assigned_pandit)

        # Check booking history page displays the record
        profile_resp = self.client.get(reverse('profile'))
        self.assertEqual(profile_resp.status_code, 200)
        self.assertContains(profile_resp, 'Ganesh Puja')
        self.assertContains(profile_resp, 'Pending Assignment')

    def test_admin_metrics_dashboard_calculations(self):
        """Verify administrative operational metrics equations match specifications."""
        # Setup scenario:
        # Pandit 1 (Ram Shastri) has a CONFIRMED booking (Currently Booked)
        # Pandit 2 (Vishnu Prasad) has NO CONFIRMED booking (Available Pool)
        
        # 1. Create a CONFIRMED booking
        Booking.objects.create(
            customer=self.customer_user,
            pooja=self.ganesh_puja,
            assigned_pandit=self.pandit_1,
            date_of_pooja=date.today() + timedelta(days=2),
            muhurat_time=time(10, 0),
            venue_address='Test Venue Varanasi',
            status='CONFIRMED'
        )

        # 2. Log in as staff admin
        self.client.login(username='admin', password='admin123')

        response = self.client.get(reverse('admin_metrics'))
        self.assertEqual(response.status_code, 200)

        # Card A: Total Active Registered Pandits = 2
        self.assertEqual(response.context['total_pandits'], 2)
        self.assertContains(response, '2') # Total

        # Card B: Currently Booked Pandits = 1 (Only Pandit 1 is assigned to a CONFIRMED booking)
        self.assertEqual(response.context['currently_booked'], 1)

        # Card C: Live Available Pool Size = Total - Currently Booked = 2 - 1 = 1 (Pandit 2 is available)
        self.assertEqual(response.context['available_pool'], 1)

    def test_interactive_pandit_assignment_action(self):
        """Verify that assigning a Pandit updates status to CONFIRMED and recalculates metrics."""
        # 1. Create a PENDING booking
        booking = Booking.objects.create(
            customer=self.customer_user,
            pooja=self.ganesh_puja,
            date_of_pooja=date.today() + timedelta(days=3),
            muhurat_time=time(8, 30),
            venue_address='Vedic Ashram Varanasi',
            status='PENDING'
        )

        # 2. Log in as admin
        self.client.login(username='admin', password='admin123')

        # 3. Post assignment action
        response = self.client.post(reverse('assign_pandit', args=[booking.id]), {'pandit_id': self.pandit_1.id})
        self.assertRedirects(response, reverse('admin_metrics'))

        # 4. Verify booking has transitioned to CONFIRMED with assigned Pandit
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'CONFIRMED')
        self.assertEqual(booking.assigned_pandit, self.pandit_1)

        # 5. Check metrics updated: Booked count should now be 1, available pool should be 1 (Total=2, Booked=1)
        metrics_resp = self.client.get(reverse('admin_metrics'))
        self.assertEqual(metrics_resp.context['currently_booked'], 1)
        self.assertEqual(metrics_resp.context['available_pool'], 1)

    def test_cancel_booking_success(self):
        """Verify that a customer can successfully cancel their pending booking."""
        self.client.login(username='durgesh', password='durgesh123')
        booking = Booking.objects.create(
            customer=self.customer_user,
            pooja=self.ganesh_puja,
            date_of_pooja=date.today() + timedelta(days=5),
            muhurat_time=time(9, 30),
            venue_address='Sigra, Varanasi',
            status='PENDING'
        )
        response = self.client.post(reverse('cancel_booking', args=[booking.id]))
        self.assertRedirects(response, reverse('profile'))
        
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'CANCELLED')

    def test_cancel_booking_unauthorized(self):
        """Verify that a customer cannot cancel another customer's booking."""
        other_user = User.objects.create_user(
            username='other_customer', email='other@gmail.com', password='otheruser123'
        )
        booking = Booking.objects.create(
            customer=other_user,
            pooja=self.ganesh_puja,
            date_of_pooja=date.today() + timedelta(days=5),
            muhurat_time=time(9, 30),
            venue_address='Some Address',
            status='PENDING'
        )
        # Login as durgesh, try to cancel other_user's booking
        self.client.login(username='durgesh', password='durgesh123')
        response = self.client.post(reverse('cancel_booking', args=[booking.id]))
        self.assertEqual(response.status_code, 404)
        
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'PENDING')

    def test_cancel_booking_invalid_status(self):
        """Verify that completed bookings cannot be cancelled."""
        self.client.login(username='durgesh', password='durgesh123')
        booking = Booking.objects.create(
            customer=self.customer_user,
            pooja=self.ganesh_puja,
            date_of_pooja=date.today() + timedelta(days=5),
            muhurat_time=time(9, 30),
            venue_address='Sigra, Varanasi',
            status='COMPLETED'
        )
        response = self.client.post(reverse('cancel_booking', args=[booking.id]))
        self.assertRedirects(response, reverse('profile'))
        
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'COMPLETED')

