from django.shortcuts import render,redirect
import requests
from LibrarySystem import settings
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages

# Create your views here.

import requests
from django.shortcuts import render

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
            # Add preview URL (Google Books previewLink)
            book['preview_url'] = book['volumeInfo'].get('previewLink', '')
    except requests.RequestException:
        books = []

    return render(request, 'home.html', {'books': books, 'query': query, 'user': request.user})






from HomePage.models import CustomUser  # Import your custom user model

def Signin(request):
    if request.method == "POST":
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')

        # Create a username using first name + last name
        username = firstname + " " + lastname

        # Check if email already exists (since email is the unique identifier in the custom model)
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("/signin")

        # Create user using CustomUser model
        user = CustomUser.objects.create_user(email=email, first_name=firstname, last_name=lastname, password=pass1,username=username)
        user.username = username  # Assign username if needed
        user.save()

        messages.success(request, "Sign-up successful! Please log in.")
        return redirect("/login")

    return render(request, 'signin.html')


def Login(request):
    if request.method == "POST":
        email = request.POST.get('emailid')  # Keep field names consistent
        pass1 = request.POST.get('pass1')

        # Authenticate using email and password (CustomUser authentication)
        user = authenticate(request, email=email, password=pass1)

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
    return render(request, 'readingpage.html', {'preview_url': volume_id})