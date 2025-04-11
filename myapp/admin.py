from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    MyUser, UserProfile, LandOwner, LandSeeker, Broker,
    AgriculturalExpertise, Land, Interest, Agreement, Payment, Report,
    LandListing
)

# Customizing the User Admin
class MyUserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ()

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone', 'address', 'pincode', 'gender', 'photo')
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

admin.site.register(MyUser, MyUserAdmin)

# Registering other models
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'address', 'pincode')

@admin.register(LandOwner)
class LandOwnerAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(LandSeeker)
class LandSeekerAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'gender', 'agricultural_expertise')

@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name')

@admin.register(AgriculturalExpertise)
class AgriculturalExpertiseAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Land)
class LandAdmin(admin.ModelAdmin):
    list_display = ('owner', 'location', 'size', 'water_availability', 'soil_type', 'is_available')
    list_filter = ('is_available', 'soil_type')
    search_fields = ('location',)

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('seeker', 'land', 'expressed_on')

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ('land', 'landowner', 'landseeker', 'broker', 'start_date', 'end_date')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('agreement', 'amount', 'paid_on', 'payment_method')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('generated_by', 'generated_on')
    search_fields = ('generated_by__email',)

@admin.register(LandListing)
class LandListingAdmin(admin.ModelAdmin):
    list_display = ('land_name', 'location', 'size', 'soil_type', 'created_at')
    search_fields = ('land_name', 'location')
