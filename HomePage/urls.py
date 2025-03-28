from django.urls import path
from HomePage import views

urlpatterns = [
    path('', views.search_books, name='search_books'),
    path('signin',views.Signin,name="signin"),
    path('login',views.Login,name="login"),
    path('logout',views.Logout,name="logout"),
    path('readingpage/', views.readingpage, name='readingpage'),
]