from django.db import models
from django.contrib.auth.models import User

class PoojaService(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    estimated_duration_hours = models.DecimalField(max_digits=3, decimal_places=1)
    base_price = models.IntegerField()
    image = models.URLField(max_length=500, blank=True, null=True, help_text="URL to service image")

    class Meta:
        verbose_name = "Pooja Service"
        verbose_name_plural = "Pooja Services"

    def __str__(self):
        return self.title


class Pandit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pandit_profile')
    phone_number = models.CharField(max_length=15)
    profile_picture = models.URLField(max_length=500, blank=True, null=True, help_text="URL to profile picture")
    languages_spoken = models.CharField(max_length=255, help_text="e.g. Hindi, Sanskrit, Marathi")
    specialization = models.ManyToManyField(PoojaService, related_name='pandits')
    base_city = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True, help_text="Global operational status tracker")

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"Pandit {full_name if full_name else self.user.username} ({self.base_city})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Assignment'),
        ('CONFIRMED', 'Pandit Assigned'),
        ('COMPLETED', 'Pooja Completed'),
        ('CANCELLED', 'Cancelled')
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_bookings')
    pooja = models.ForeignKey(PoojaService, on_delete=models.PROTECT, related_name='bookings')
    assigned_pandit = models.ForeignKey(Pandit, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    date_of_pooja = models.DateField()
    muhurat_time = models.TimeField()
    venue_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_of_pooja', 'muhurat_time']

    def __str__(self):
        return f"{self.pooja.title} on {self.date_of_pooja} at {self.muhurat_time} - {self.get_status_display()}"
