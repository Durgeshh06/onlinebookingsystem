from django.contrib import admin
from .models import PoojaService, Pandit, Booking

@admin.register(PoojaService)
class PoojaServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'estimated_duration_hours', 'base_price')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')


@admin.register(Pandit)
class PanditAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'phone_number', 'base_city', 'is_available')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number', 'base_city', 'languages_spoken')
    list_filter = ('is_available', 'base_city')
    filter_horizontal = ('specialization',)

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_name.short_description = 'Pandit Name'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'pooja', 'customer', 'assigned_pandit', 'date_of_pooja', 'muhurat_time', 'status')
    list_filter = ('status', 'date_of_pooja')
    search_fields = ('customer__username', 'venue_address', 'pooja__title')
    raw_id_fields = ('customer', 'assigned_pandit')
