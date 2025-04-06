from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta
from django.http import JsonResponse
import requests
from LibrarySystem import settings
from HomePage.models import CustomUser, UserProfile

# Book Search Function
def search_books(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return render(request, 'home.html', {'books': [], 'query': '', 'user': request.user})

    api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&startIndex=0&maxResults=20"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        books = response.json().get('items', [])
        for book in books:
            book['preview_url'] = book['volumeInfo'].get('previewLink', '')
    except requests.RequestException:
        books = []

    return render(request, 'home.html', {'books': books, 'query': query, 'user': request.user})


# Sign In and Sign Up Functions
def Signin(request):
    if request.method == "POST":
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')

        username = f"{firstname} {lastname}"

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("/signin")

        user = CustomUser.objects.create_user(email=email, first_name=firstname, last_name=lastname, password=pass1, username=username)
        user.save()

        messages.success(request, "Sign-up successful! Please log in.")
        return redirect("/login")

    return render(request, 'signin.html')


from django.contrib.auth import authenticate, login
import logging

logger = logging.getLogger(__name__)

def Login(request):
    if request.method == "POST":
        email = request.POST.get('emailid')
        pass1 = request.POST.get('pass1')

        user = authenticate(request, username=email, password=pass1)
        logger.debug(f"Trying to authenticate user: {email}, Result: {user}")

        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful")
            return redirect("/")
        else:
            messages.error(request, "Invalid email/password")
            return redirect('/login')

    return render(request, 'login.html')



def Logout(request):
    logout(request)
    messages.info(request, "Logout successful")
    return redirect("/")

def readingpage(request):
    preview_url = request.GET.get('preview_url', '')  # Get the full preview URL
    volume_id = preview_url.split('id=')[-1]  # Extract the Volume ID
    return render(request, 'subscription.html', {'preview_url': volume_id})

from django.utils import timezone


def Subscription(request):
    current_plan = 'free'
    expiry_date = None
    is_upgradeable = False
    show_monthly = True  # Default to showing both plans for guests

    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        current_plan = profile.subscription
        expiry_date = profile.subscription_expiry
        is_upgradeable = current_plan == 'monthly' or current_plan == 'free'
        show_monthly = current_plan == 'free'

    return render(request, 'subscription.html', {
        'user': request.user,
        'current_plan': current_plan,
        'expiry_date': expiry_date,
        'is_upgradeable': is_upgradeable,
        'show_monthly': show_monthly,
    })




# Subscription and Payment Handling

from datetime import timedelta, date

@login_required
def payment_success(request):
    order_id = request.GET.get('order_id')
    plan = request.GET.get('plan', 'monthly')

    if order_id:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        today = date.today()

        # Only allow upgrades
        if profile.subscription == 'yearly':
            messages.info(request, "You already have a Yearly plan.")
            return redirect('/subscription')

        # Set expiry accordingly
        if plan == 'monthly':
            profile.subscription = 'monthly'
            profile.subscription_expiry = today + timedelta(days=30)
        elif plan == 'yearly':
            profile.subscription = 'yearly'
            profile.subscription_expiry = today + timedelta(days=365)

        profile.save()
        messages.success(request, f"{plan.capitalize()} plan activated successfully.")
    else:
        messages.error(request, "Payment failed or missing order ID.")

    return redirect('/subscription')




# Get Payment Session (AJAX call)
from django.http import JsonResponse

@login_required
def get_session(request):
    Cashfree.XClientId = settings.CASHFREE_APP_ID
    Cashfree.XClientSecret = settings.CASHFREE_SECRET_KEY
    Cashfree.XEnvironment = Cashfree.SANDBOX
    x_api_version = "2023-08-01"

    plan = request.GET.get('plan', 'yearly')
    price = 739.0 if plan == 'yearly' else 69.0

    email_prefix = request.user.email.split('@')[0]# Use the part before '@' as prefix
    customer = CustomerDetails(
        customer_id = f"user_{request.user.id}_{email_prefix}",
        customer_email=request.user.email,
        customer_phone="9999999999",
        customer_name=request.user.username or request.user.email
    )

    # Create a dynamic return URL based on the request
    return_url = f"{request.build_absolute_uri('/payment_success/')}?order_id={{order_id}}&plan={plan}"

    order_meta = OrderMeta(
        return_url=return_url  # Pass the return_url to the order meta
    )

    create_order_request = CreateOrderRequest(
        order_amount=price,
        order_currency="INR",
        customer_details=customer,
        order_meta=order_meta,
    )

    try:
        api_response = Cashfree().PGCreateOrder(x_api_version, create_order_request, None, None)
        payment_session_id = api_response.data.payment_session_id

        # Return payment session ID and return URL to frontend
        return JsonResponse({'paymentSessionId': payment_session_id, 'returnUrl': return_url})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def cancel_subscription(request):
    if request.method == "POST":
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Reset subscription
        profile.subscription = 'free'
        profile.subscription_expiry = None
        profile.save()

        messages.success(request, "Your subscription has been cancelled.")
    return redirect('/subscription')



