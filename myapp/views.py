from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_backends
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from .utils import render_to_pdf
from .models import Notification
from django.http import HttpResponseForbidden  #
from django.contrib import messages
from django.utils import timezone
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from .models import Interest
from .models import (
    MyUser, LandOwner, LandSeeker, Broker,
    Land, Interest, Message,Report,Agreement,LandListing,Payment
)

# ---------- Public Views ----------

def index(request):
    return render(request, 'index.html')

def services(request):
    return render(request, 'services.html')

def contact(request):
    return render(request, 'contact.html')

def faq(request):
    return render(request, 'faq.html')

def about(request):
    return render(request, 'about.html')

def newland_view(request):
    # your logic here
    return render(request, 'newland.html')

def agreements_view(request):
    # your logic here
    return render(request, 'agreements.html')

def mylands_view(request):
    # your logic here
    return render(request, 'mylands.html')
def payment1(request):
    # your logic here
 # Adjust based on user type
    return render(request, 'payment.html')
   

def landowners_list(request):
    landowners = LandOwner.objects.all()
    return render(request, 'landowners_list.html', {'landowners': landowners})
@login_required
def landseekers_list(request):
    landseekers = LandSeeker.objects.all().select_related('user')
    return render(request, 'landseekers_list.html', {'landseekers': landseekers})


def landowner_detail(request, pk):
    landowner = get_object_or_404(LandOwner, pk=pk)
    return render(request, 'landowner_detail.html', {'landowner': landowner})

def verify_landowners(request):
    pending = LandOwner.objects.filter(verified=False)
    if request.method == 'POST':
        landowner_id = request.POST.get('landowner_id')
        landowner = LandOwner.objects.get(pk=landowner_id)
        landowner.verified = True
        landowner.save()
    return render(request, 'verify_landowners.html', {'pending': pending})

@login_required
def view_landseeker_profile(request, seeker_id):
    seeker = get_object_or_404(LandSeeker, id=seeker_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            seeker.status = 'Approved'
            seeker.approved_by = request.user
        elif action == 'reject':
            seeker.status = 'Rejected'
            seeker.approved_by = request.user
        seeker.save()
        messages.success(request, f'Landseeker {action}d successfully.')
        return redirect('landseekers_list')

    return render(request, 'view_landseeker_profile.html', {'seeker': seeker})


@require_POST
@login_required
def approve_landowner(request, user_id):
    landowner = get_object_or_404(LandOwner, user_id=user_id)
    landowner.verified = True
    landowner.save()
    # Create notification
    Notification.objects.create(
        user=landowner.user,
        message="Your landowner profile has been approved by the broker. You can now list your land."
    )

    messages.success(request, f"{landowner.user.first_name} has been approved successfully.")
    return redirect('landowners_list')
    return redirect('landowners_list')  # Adjust to your actual list view name

@require_POST
@login_required
def reject_landowner(request, user_id):
    landowner = get_object_or_404(LandOwner, user_id=user_id)
    landowner.delete()  # or set a status flag if you prefer
    return redirect('landowners_list')

@login_required
def approve_landseeker(request, landseeker_id):
    landseeker = get_object_or_404(LandSeeker, id=landseeker_id)
    broker = Broker.objects.get(user=request.user)
    
    landseeker.status = 'Approved'
    landseeker.approved_by = broker
    landseeker.save()

    # Create notification
    Notification.objects.create(
        user=landseeker.user,
        message="✅ Your landseeker profile has been approved by the broker."
    )

    messages.success(request, "Landseeker approved.")
    return redirect('broker_dashboard')


@login_required
def reject_landseeker(request, landseeker_id):
    landseeker = get_object_or_404(LandSeeker, id=landseeker_id)
    
    landseeker.status = 'Rejected'
    landseeker.approved_by = None
    landseeker.save()

    # Create notification
    Notification.objects.create(
        user=landseeker.user,
        message="❌ Your landseeker profile has been rejected by the broker."
    )

    messages.warning(request, "Landseeker rejected.")
    return redirect('broker_dashboard')




# ---------- Authentication ----------

class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')
    
    def post(self, request):
        data = request.POST
        photo = request.FILES.get('photo')

        if MyUser.objects.filter(email=data['email']).exists():
            return render(request, 'register.html', {'error': 'Email already exists.'})

        try:
            user = MyUser.objects.create_user(
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data['phone'],
                address=data['address'],
                pincode=data['pincode'],
                gender=data['gender'],
                photo=photo
            )

            role = data['role']
            if role == 'landowner':
                LandOwner.objects.create(user=user)
            elif role == 'landseeker':
                LandSeeker.objects.create(user=user)
            elif role == 'broker':
                Broker.objects.create(user=user)

            user.backend = get_backends()[0].__class__.__module__ + '.' + get_backends()[0].__class__.__name__
            login(request, user)
            return redirect(f'/{role}/dashboard')

        except IntegrityError:
            return render(request, 'register.html', {'error': 'Registration error. Try again.'})

class CustomLoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        if user:
            # Log the user in and set the session
            login(request, user)
            # Redirect based on the user's role
            if hasattr(user, 'landowner'):
                return redirect('/landowner/dashboard')
            elif hasattr(user, 'landseeker'):
                return redirect('/landseeker/dashboard')
            elif hasattr(user, 'broker'):
                return redirect('/broker/dashboard')
        else:
            # If authentication fails, show an error message
            return render(request, 'login.html', {'error': 'Invalid email or password'})

class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

def register(request):
    if request.method == 'POST':
        data = request.POST
        photo = request.FILES.get('photo')

        if MyUser.objects.filter(email=data['email']).exists():
            return render(request, 'register.html', {'error': 'Email already exists.'})

        try:
            user = MyUser.objects.create_user(
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data['phone'],
                address=data['address'],
                pincode=data['pincode'],
                gender=data['gender'],
                photo=photo
            )

            role = data['role']
            if role == 'landowner':
                LandOwner.objects.create(user=user)
            elif role == 'landseeker':
                LandSeeker.objects.create(user=user)
            elif role == 'broker':
                Broker.objects.create(user=user)

            user.backend = get_backends()[0].__class__.__module__ + '.' + get_backends()[0].__class__.__name__
            login(request, user)
            return redirect(f'/{role}/dashboard')

        except IntegrityError:
            return render(request, 'register.html', {'error': 'Registration error. Try again.'})

    return render(request, 'register.html')



def custom_logout(request):
    logout(request)
    return redirect('login')

def logout1(request):
    logout(request)
    return redirect('index')

# ---------- Admin Views ----------

def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, 'Invalid email or password')
            return render(request, 'admin_login.html')
        
        if not user.is_superuser:
            messages.error(request, 'You do not have admin privileges')
            return render(request, 'admin_login.html')
        
        if not user.is_active:
            messages.error(request, 'This account is inactive')
            return render(request, 'admin_login.html')

        login(request, user)
        return redirect('admin_dashboard')

    return render(request, 'admin_login.html')

@user_passes_test(lambda u: u.is_superuser)
@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@user_passes_test(lambda u: u.is_superuser)
@login_required
def manage_users(request):
    users = MyUser.objects.all()
    return render(request, 'admin/manage_users.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_staff)
def generate_reports(request):
    # Get user statistics
    total_users = MyUser.objects.count()
    landowners_count = MyUser.objects.filter(role='landowner').count()
    landseekers_count = MyUser.objects.filter(role='landseeker').count()
    brokers_count = MyUser.objects.filter(role='broker').count()

    # Get land statistics
    total_lands = LandListing.objects.count()
    total_interests = Interest.objects.count()
    total_agreements = Agreement.objects.count()

    context = {
        'total_users': total_users,
        'landowners_count': landowners_count,
        'landseekers_count': landseekers_count,
        'brokers_count': brokers_count,
        'total_lands': total_lands,
        'total_interests': total_interests,
        'total_agreements': total_agreements,
    }

    return render(request, 'admin/generate_reports.html', context)

# ---------- Dashboards ----------

@login_required
def broker_dashboard(request):
    broker = get_object_or_404(Broker, user=request.user)
    agreements = Agreement.objects.filter(broker=broker)
    payments = Payment.objects.filter(agreement__broker=broker)
    return render(request, 'broker_dashboard.html', {'agreements': agreements, 'payments': payments})


@login_required
def landowner_dashboard(request):
    # Ensure the user has a landowner profile
    if not hasattr(request.user, 'landowner'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('index')
    
    # Fetch related data
    lands = Land.objects.filter(owner=request.user.landowner)
    interests = Interest.objects.filter(land__owner=request.user.landowner)
    
    # Fetch unread notifications and count them
    unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    # Fetch all notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')

    # Pass all context to the template
    return render(request, 'landowner_dashboard.html', {
        'lands': lands,
        'interests': interests,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,  # Pass the count to the template
    })

def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.save()
    return redirect('landowner_dashboard')  # Redirect back to dashboard


@login_required
def landseeker_dashboard(request):
    if not hasattr(request.user, 'landseeker'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('index')
    
    landseeker = request.user.landseeker
    # Get the list of interests for the current landseeker
    interests = Interest.objects.filter(seeker=landseeker)
    
    # Get all available lands that the landseeker has not expressed interest in
    available_lands = Land.objects.filter(is_available=True).select_related('owner')
    
    return render(request, 'landseeker_dashboard.html', {
        'landseeker': landseeker,
        'interests': interests,
        'available_lands': available_lands
    })

# ---------- Land Actions ----------

@login_required
def express_interest(request, land_id):
    land = get_object_or_404(Land, id=land_id)
    landseeker = request.user.landseeker
    
    # Check if interest already exists
    existing_interest = Interest.objects.filter(seeker=landseeker, land=land).first()
    if existing_interest:
        messages.info(request, 'You have already expressed interest in this land.')
    else:
        # Create new interest
        Interest.objects.create(
            seeker=landseeker, 
            land=land, 
            expressed_on=timezone.now(),
            status='pending'
        )
        messages.success(request, 'Interest expressed successfully! The landowner will be notified.')
    
    return redirect('land_details', pk=land_id)

def withdraw_interest(request, interest_id):
    # Get the interest object based on the ID
    interest = get_object_or_404(Interest, id=interest_id)

    # Check if the logged-in user is the seeker associated with this interest
    if interest.seeker == request.user:
        # Update the status of the interest to 'withdrawn' (or similar)
        interest.status = 'withdrawn'
        interest.save()
        # Redirect the user to the page displaying their interests
        return redirect('my_interests')
    else:
        # If the user does not own the interest, return an error or redirect
        return redirect('error_page')  # Replace 'error_page' with an actual URL name

@login_required
def add_land(request):
    if request.method == 'POST':
        # Make sure the 'land_name' key is now present in POST data
        land_name = request.POST['land_name']  # This should work now
        Land.objects.create(
            owner=request.user.landowner,
            land_name=land_name,
            location=request.POST['location'],
            size=request.POST['size'],
            soil_type=request.POST['soil_type'],
            water_availability=request.POST.get('water_availability') == 'on',
            is_available=request.POST.get('is_available') == 'on',
            price=request.POST.get('price'),
            description=request.POST.get('description'),
            image=request.FILES.get('image')
        )
        return redirect('view_my_lands')  # Or your intended URL name
    return render(request, 'add_land.html')





@login_required
def edit_land(request, land_id):
    try:
        landowner = LandOwner.objects.get(user=request.user)
        land = Land.objects.get(id=land_id, owner=landowner)
        
        if request.method == 'POST':
            # Process form submission
            land.location = request.POST.get('location')
            land.size = request.POST.get('size')
            soil_type = request.POST.get('soil_type')
            
            # Validate soil_type is not empty
            if not soil_type:
                messages.error(request, 'Soil type is required.')
                return render(request, 'edit_land.html', {'land': land})
                
            land.soil_type = soil_type
            land.water_availability = request.POST.get('water_availability') == 'on'
            land.is_available = request.POST.get('is_available') == 'on'
            
            # Handle price field
            price = request.POST.get('price')
            if price:
                try:
                    land.price = float(price)
                except ValueError:
                    messages.error(request, 'Price must be a valid number.')
                    return render(request, 'edit_land.html', {'land': land})
            
            # Handle description field
            land.description = request.POST.get('description', '')
            
            # Handle image upload
            if 'image' in request.FILES:
                land.image = request.FILES['image']
            
            try:
                land.save()
                messages.success(request, 'Land updated successfully!')
                return redirect('view_my_lands')
            except Exception as e:
                messages.error(request, f'Error saving land: {str(e)}')
                return render(request, 'edit_land.html', {'land': land})
        
        return render(request, 'edit_land.html', {'land': land})
    except LandOwner.DoesNotExist:
        messages.error(request, 'You do not have permission to edit this land.')
        return redirect('index')
    except Land.DoesNotExist:
        messages.error(request, 'Land not found.')
        return redirect('view_my_lands')

@login_required
def delete_land(request, land_id):
    try:
        landowner = LandOwner.objects.get(user=request.user)
        land = get_object_or_404(Land, id=land_id, owner=landowner)
        if request.method == "POST":
            land.delete()
            messages.success(request, 'Land deleted successfully!')
            return redirect('view_my_lands')
        return render(request, 'confirm_delete_land.html', {'land': land})
    except LandOwner.DoesNotExist:
        messages.error(request, 'You do not have permission to delete lands.')
        return redirect('view_my_lands')

def land_details(request, pk):
    land = get_object_or_404(Land, id=pk)
    interests = Interest.objects.filter(land=land)
    
    # Check if user is the landowner
    is_landowner = hasattr(request.user, 'landowner') and request.user.landowner == land.owner
    
    # Check if user is a broker
    is_broker = hasattr(request.user, 'broker')
    
    # Get all brokers for potential connection
    brokers = Broker.objects.all()
    
    context = {
        'land': land, 
        'interests': interests,
        'is_landowner': is_landowner,
        'is_broker': is_broker,
        'brokers': brokers
    }
    
    return render(request, 'land_details.html', context)
@login_required
def view_my_lands(request):
    try:
        landowner = LandOwner.objects.get(user=request.user)
        lands = Land.objects.filter(owner=landowner)
        return render(request, 'view_my_lands.html', {'lands': lands})
    except LandOwner.DoesNotExist:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('index')

def land_search(request):
       query = request.GET.get('q')  # Corrected to match the form input name
       lands = Land.objects.filter(is_available=True)
       if query:
           lands = lands.filter(location__icontains=query)
       return render(request, 'land_search.html', {'lands': lands})

@login_required
def land_list(request):
    """
    View for displaying available agricultural lands
    - Requires login
    - Shows different data based on user type (owner vs buyer)
    - Filters only available lands
    """
    
    # Check if user has landowner profile
    is_landowner = hasattr(request.user, 'landowner')
    
    # Get available lands with related owner data
    available_lands = Land.objects.filter(
        is_available=True
    ).select_related('owner__user')  # Optimizes database queries
    
    # Add owner filter if user is a landowner
    if is_landowner:
        available_lands = available_lands.filter(
            owner=request.user.landowner
        )
        template_title = "My Available Lands"
    else:
        template_title = "Browse Available Lands"
    
    context = {
        'available_lands': available_lands,
        'page_title': template_title,
        'is_landowner': is_landowner
    }
    
    return render(request, 'land_list.html', context)


# ---------- Messaging ----------
@login_required
def send_message(request, landowner_id):
    if request.method == "POST":
        content = request.POST.get('content')
        message = Message(sender=request.user.landseeker, receiver=LandOwner.objects.get(id=landowner_id), content=content)
        message.save()
        messages.success(request, 'Message sent successfully!')
        return redirect('view_messages')

@login_required
def view_messages(request):
    messages = Message.objects.filter(receiver=request.user.landowner)  # Adjust based on user type
    return render(request, 'view_messages.html', {'messages': messages})

# ---------- Agreements ----------
@login_required
def create_agreement(request, land_id):
    if request.method == "POST":
        land = get_object_or_404(Land, id=land_id)
        agreement = Agreement(
            land=land,
            landowner=land.owner,
            landseeker=request.user.landseeker,
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            terms=request.POST.get('terms')
        )
        agreement.save()
        messages.success(request, 'Agreement created successfully!')
        return redirect('view_agreements')

@login_required
def accept_agreement(request, agreement_id):
    agreement = get_object_or_404(Agreement, id=agreement_id)
    agreement.status = 'accepted'  # Assuming you have a status field
    agreement.save()
    messages.success(request, 'Agreement accepted successfully!')
    return redirect('view_agreements')

@login_required
def make_payment(request, agreement_id):
    if request.method == "POST":
        amount = request.POST.get('amount')
        payment = Payment(
            agreement=Agreement.objects.get(id=agreement_id),
            amount=amount,
            payment_method=request.POST.get('payment_method')
        )
        payment.save()
        messages.success(request, 'Payment made successfully!')
        return redirect('view_payments')

@login_required
def generate_report(request, agreement_id):
    if request.method == "POST":
        agreement = get_object_or_404(Agreement, id=agreement_id)
        report_content = f"Agreement for {agreement.land.location} between {agreement.landseeker} and {agreement.landowner}."
        report = Report(generated_by=request.user, content=report_content)
        report.save()
        messages.success(request, 'Report generated successfully!')
        return redirect('view_reports')

@login_required
def view_report(request):
    reports = Report.objects.all()  # Fetch all reports
    return render(request, 'view_reports.html', {'reports': reports})

# ---------- LandOwner Profile ----------

@login_required
def landowner_profile(request):
    try:
        # Correcting the query to use 'user' or 'user_id' instead of 'userid'
        landowner = LandOwner.objects.get(user=request.user)  # Use 'user' field to get the landowner
    except LandOwner.DoesNotExist:
        landowner = None

    return render(request, 'landowner_profile.html', {'landowner': landowner})

@login_required
def edit_landowner_profile(request):
    try:
        landowner = LandOwner.objects.get(user=request.user)
    except LandOwner.DoesNotExist:
        return redirect('landowner_profile')

    if request.method == 'POST':
        # Update LandOwner fields
        landowner.address = request.POST.get('address', landowner.address)
        landowner.phone = request.POST.get('phone', landowner.phone)
        landowner.gender = request.POST.get('gender', landowner.gender)
        landowner.pincode = request.POST.get('pincode', landowner.pincode)

        # Update User fields
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)

        # Save user
        request.user.save()

        # Handle uploaded photo
        if 'photo' in request.FILES:
            landowner.photo = request.FILES['photo']

        # Save landowner
        landowner.save()

        return redirect('landowner_profile')

    return render(request, 'edit_landowner_profile.html', {'landowner': landowner})

    
# ---------- LandSeeker Profile ----------

@login_required
def landseeker_profile(request):
    if not hasattr(request.user, 'landseeker'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('index')
    
    landseeker = request.user.landseeker
    return render(request, 'landseeker_profile.html', {'landseeker': landseeker})

@login_required
def edit_landseeker_profile(request):
    landseeker = get_object_or_404(LandSeeker, user=request.user)
    if request.method == 'POST':
        landseeker.first_name = request.POST.get('first_name')
        landseeker.last_name = request.POST.get('last_name')
        landseeker.date_of_birth = request.POST.get('date_of_birth')
        landseeker.address = request.POST.get('address')
        landseeker.gender = request.POST.get('gender')
        landseeker.crop_requirement = request.POST.get('crop_requirement')
        landseeker.desired_land_size = request.POST.get('desired_land_size')

        if request.FILES.get('photo'):
            landseeker.photo = request.FILES['photo']

        landseeker.save()
        return redirect('landseeker_profile')

    return render(request, 'edit_landseeker_profile.html', {'landseeker': landseeker})

# ---------- Listings (Land Posts) ----------

@login_required
def add_land_listing1(request):
    if request.method == "POST":
        listing = LandListing(
            owner=request.user,
            land_name=request.POST.get('land_name'),
            location=request.POST.get('location'),
            size=request.POST.get('size'),
            soil_type=request.POST.get('soil_type'),
            water_availability=request.POST.get('water_availability'),
            image=request.FILES.get('image'),
            description=request.POST.get('description')
        )
        listing.save()
        return redirect('landowner_dashboard')
    return render(request, 'add_land_listing.html')

@login_required
def manage_listings(request):
    listings = LandListing.objects.filter(owner=request.user)
    return render(request, 'manage_listings.html', {'listings': listings})

@login_required
def land_listing_list(request):
    # Filter listings by the logged-in user
    listings = LandListing.objects.filter(owner=request.user)
    return render(request, 'viewland.html', {'listings': listings})  # Ensure this line is correct


class LandListingView(LoginRequiredMixin, ListView):
    model = LandListing
    template_name = 'land_list.html'
    context_object_name = 'available_lands'
    ordering = ['-created_at']

    def get_queryset(self):
        """Return available lands with optional owner filtering."""
        queryset = LandListing.objects.filter(is_available=True)

        if hasattr(self.request.user, 'landowner'):
            queryset = queryset.filter(owner=self.request.user)

        return queryset.select_related('owner')

    def get_context_data(self, **kwargs):
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = "My Land Listings" if hasattr(self.request.user, 'landowner') else "Available Lands"
        context['is_landowner'] = hasattr(self.request.user, 'landowner')
        return context

    
@login_required
def my_interests(request):
    if hasattr(request.user, 'landseeker'):
        interests = Interest.objects.filter(seeker=request.user.landseeker)
    else:
        interests = []  # or redirect to an error page

    return render(request, 'my_interests.html', {'interests': interests})

class MyInterestsView(ListView):
    model = Interest
    template_name = 'my_interests.html'
    context_object_name = 'interests'
    
    def get_queryset(self):
        if hasattr(self.request.user, 'landseeker'):
            return Interest.objects.filter(seeker=self.request.user.landseeker).order_by('-expressed_on')
        return Interest.objects.none()
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'landseeker'):
            messages.error(request, 'Only land seekers can view interests.')
            return redirect('index')
        return super().get(request, *args, **kwargs)
    
    

@login_required
def add_land_listing(request):
    if request.method == 'POST':
        land_name = request.POST.get('land_name')
        location = request.POST.get('location')
        size = request.POST.get('size')
        soil_type = request.POST.get('soil_type')
        water_availability = request.POST.get('water_availability')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        listing = LandListing.objects.create(
            owner=request.user,
            land_name=land_name,
            location=location,
            size=size,
            soil_type=soil_type,
            water_availability=water_availability,
            description=description,
            image=image
        )
        
        messages.success(request, 'Land listing added successfully!')
        return redirect('manage_listings')
    
    return render(request, 'add_land_listing.html')

@login_required
def handle_interest(request, interest_id, action):
    interest = get_object_or_404(Interest, id=interest_id)
    land = interest.land
    
    # Check if user is the landowner
    if not hasattr(request.user, 'landowner') or request.user.landowner != land.owner:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('land_details', pk=land.id)
    
    if action == 'accept':
        interest.status = 'accepted'
        interest.save()
        messages.success(request, f'Interest from {interest.seeker.user.first_name} has been accepted.')
    elif action == 'reject':
        interest.status = 'rejected'
        interest.save()
        messages.info(request, f'Interest from {interest.seeker.user.first_name} has been rejected.')
    
    return redirect('land_details', pk=land.id)

@login_required
def broker_facilitate_connection(request, interest_id):
    interest = get_object_or_404(Interest, id=interest_id)
    land = interest.land
    
    # Check if user is a broker
    if not hasattr(request.user, 'broker'):
        messages.error(request, 'Only brokers can facilitate connections.')
        return redirect('land_details', pk=land.id)
    
    # Check if interest is accepted
    if interest.status != 'accepted':
        messages.error(request, 'Can only facilitate connections for accepted interests.')
        return redirect('land_details', pk=land.id)
    
    if request.method == 'POST':
        # Create agreement
        agreement = Agreement.objects.create(
            land=land,
            landowner=land.owner,
            landseeker=interest.seeker,
            broker=request.user.broker,
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            terms=request.POST.get('terms', 'Standard terms apply')
        )
        
        # Create initial payment
        Payment.objects.create(
            agreement=agreement,
            amount=request.POST.get('amount', 5000),
            paid_on=timezone.now(),
            payment_method=request.POST.get('payment_method', 'Cash')
        )
        
        # Update interest status
        interest.status = 'connected'
        interest.save()
        
        messages.success(request, 'Connection facilitated successfully!')
        return redirect('broker_dashboard')
    
    # If GET request, show the form
    return render(request, 'broker_facilitate.html', {
        'interest': interest,
        'land': land,
        'seeker': interest.seeker
    })
@login_required
def approve_interest(request, interest_id):
    interest = get_object_or_404(Interest, id=interest_id)
    if request.user != interest.land.owner.user:
        return HttpResponseForbidden("Not authorized.")
    if request.method == 'POST':
        interest.status = 'accepted'
        interest.save()
    return redirect('landowner_dashboard')

@login_required
def view_lands(request, landowner_id=None):
    if landowner_id:
        landowner = get_object_or_404(LandOwner, id=landowner_id)
        lands = Land.objects.filter(owner=landowner)
    else:
        lands = Land.objects.all()

    return render(request, 'view_lands.html', {'lands': lands})


def view_interest_details(request, interest_id):
    interest = get_object_or_404(Interest, id=interest_id)
    seeker = interest.seeker
    land = interest.land
    return render(request, 'interest_details.html', {
        'seeker': seeker,
        'land': land,
        'interest': interest,
    })

@login_required
def send_message(request, user_id):
    user = get_object_or_404(MyUser, id=user_id)
    return render(request, 'send_message.html', {'receiver': user})


def inbox(request):
    messages = Message.objects.filter(receiver=request.user)
    return render(request, 'inbox.html', {'messages': messages})

class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        data = {
            'title': 'Land Details PDF',
            'lands': Land.objects.all()
        }
        return render_to_pdf('land_pdf.html', data)