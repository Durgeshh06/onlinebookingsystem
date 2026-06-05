from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from datetime import datetime

from .models import PoojaService, Pandit, Booking

# ==========================================
# CUSTOMER VIEWS
# ==========================================

def home(request):
    """Landing Page displaying promotional banners and popular poojas."""
    popular_services = PoojaService.objects.all()[:3]
    return render(request, 'bookings/home.html', {'services': popular_services})


def catalog(request):
    """Grid catalog layout displaying all available PoojaServices."""
    query = request.GET.get('q', '')
    if query:
        services = PoojaService.objects.filter(title__icontains=query) | PoojaService.objects.filter(description__icontains=query)
    else:
        services = PoojaService.objects.all()
    
    return render(request, 'bookings/catalog.html', {'services': services, 'query': query})


def detail(request, slug):
    """Detail view of a specific pooja with durations, prices, and CTA to book."""
    service = get_object_or_404(PoojaService, slug=slug)
    # Fetch certified pandits specialized in this pooja for high social proof
    specialized_pandits = Pandit.objects.filter(specialization=service, is_available=True)[:3]
    return render(request, 'bookings/detail.html', {
        'service': service,
        'pandits': specialized_pandits
    })


@login_required
def book(request, slug):
    """Booking checkout multi-step form (Date, Time, Address)."""
    service = get_object_or_404(PoojaService, slug=slug)
    
    if request.method == 'POST':
        date_str = request.POST.get('date_of_pooja')
        time_str = request.POST.get('muhurat_time')
        venue_address = request.POST.get('venue_address')
        
        # Validations
        if not date_str or not time_str or not venue_address:
            messages.error(request, "All fields are required.")
            return render(request, 'bookings/book.html', {'service': service})
            
        try:
            # Parse and validate dates/times
            date_val = datetime.strptime(date_str, '%Y-%m-%d').date()
            time_val = datetime.strptime(time_str, '%H:%M').time()
            
            if date_val < datetime.today().date():
                messages.error(request, "Pooja date cannot be in the past.")
                return render(request, 'bookings/book.html', {'service': service})
                
            # Create Booking
            booking = Booking.objects.create(
                customer=request.user,
                pooja=service,
                date_of_pooja=date_val,
                muhurat_time=time_val,
                venue_address=venue_address,
                status='PENDING'
            )
            
            messages.success(request, f"Booking for {service.title} submitted successfully! A Pandit will be assigned shortly.")
            return redirect('profile')
            
        except ValueError:
            messages.error(request, "Invalid date or time format.")
            return render(request, 'bookings/book.html', {'service': service})
            
    return render(request, 'bookings/book.html', {'service': service})


@login_required
def profile(request):
    """Customer order history page showing confirmation and booking status."""
    user_bookings = Booking.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'bookings/profile.html', {'bookings': user_bookings})


@login_required
def cancel_booking(request, booking_id):
    """Allow customer to cancel their booking if it is PENDING or CONFIRMED."""
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
        if booking.status in ['PENDING', 'CONFIRMED']:
            booking.status = 'CANCELLED'
            booking.save()
            messages.success(request, f"Booking for {booking.pooja.title} has been successfully cancelled.")
        else:
            messages.error(request, "This booking cannot be cancelled.")
    return redirect('profile')




# ==========================================
# ADMINISTRATIVE DASHBOARD VIEWS
# ==========================================

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin, login_url='login')
def admin_metrics(request):
    """Restricted internal operations dashboard for platform tracking."""
    # Metric A: Total Active Registered Pandits
    total_pandits = Pandit.objects.count()
    
    # Metric B: Currently Booked Pandits
    # (Count of unique Pandits tied to bookings where status='CONFIRMED')
    booked_pandits_ids = Booking.objects.filter(status='CONFIRMED').values_list('assigned_pandit', flat=True).distinct().exclude(assigned_pandit__isnull=True)
    currently_booked_count = booked_pandits_ids.count()
    
    # Metric C: Live Available Pool Size (Total minus Currently Booked)
    live_available_pool = max(0, total_pandits - currently_booked_count)
    
    # List of all upcoming bookings sorted chronologically by date
    upcoming_bookings = Booking.objects.all().order_by('date_of_pooja', 'muhurat_time')
    
    # To facilitate interactive assignment, pass available pandits for each pending booking
    # Get all active available pandits
    all_available_pandits = Pandit.objects.filter(is_available=True)
    
    # Structure data with candidate pandits pre-filtered for convenience
    bookings_data = []
    for b in upcoming_bookings:
        candidates = []
        if b.status in ['PENDING', 'CONFIRMED']:
            # Candidates must specialize in this pooja and not be booked already on the same date (excluding this booking itself)
            conflict_pandit_ids = Booking.objects.filter(
                date_of_pooja=b.date_of_pooja, 
                status='CONFIRMED'
            ).exclude(id=b.id).values_list('assigned_pandit_id', flat=True)
            
            candidates = all_available_pandits.filter(
                specialization=b.pooja
            ).exclude(id__in=conflict_pandit_ids)
            
        bookings_data.append({
            'booking': b,
            'candidates': candidates
        })

    return render(request, 'bookings/admin_metrics.html', {
        'total_pandits': total_pandits,
        'currently_booked': currently_booked_count,
        'available_pool': live_available_pool,
        'bookings_data': bookings_data
    })


@user_passes_test(is_admin, login_url='login')
def assign_pandit(request, booking_id):
    """Action endpoint to assign a Pandit and transition status to CONFIRMED."""
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        pandit_id = request.POST.get('pandit_id')
        
        if not pandit_id:
            messages.error(request, "Please select a valid Pandit.")
            return redirect('admin_metrics')
            
        pandit = get_object_or_404(Pandit, id=pandit_id)
        booking.assigned_pandit = pandit
        booking.status = 'CONFIRMED'
        booking.save()
        
        messages.success(request, f"Pandit {pandit.user.get_full_name() or pandit.user.username} has been assigned to booking #{booking.id}.")
        
    return redirect('admin_metrics')


# ==========================================
# AUTHENTICATION VIEWS
# ==========================================

def login_user(request):
    """Authenticate existing users."""
    if request.user.is_authenticated:
        return redirect('profile')
        
    next_url = request.GET.get('next', 'profile')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'bookings/login.html')
            
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'bookings/login.html', {'next': next_url})


def register_user(request):
    """Register retail customers."""
    if request.user.is_authenticated:
        return redirect('profile')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if not username or not password or not email:
            messages.error(request, "Username, email, and password are required.")
            return render(request, 'bookings/register.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'bookings/register.html')
            
        # Create User
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Log User In
        login(request, user)
        messages.success(request, f"Account created successfully! Welcome to DevBhoomi, {first_name or username}!")
        return redirect('profile')
        
    return render(request, 'bookings/register.html')


def logout_user(request):
    """Log out currently active session."""
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')
