from django.urls import path
from HomePage import views
from HomePage import tests
urlpatterns = [
    path('', views.search_books, name='search_books'),
    path('signin',views.Signin,name="signin"),
    path('login',views.Login,name="login"),
    path('logout',views.Logout,name="logout"),
    path('subscription',views.Subscription,name="subscription"),
    path('readingpage/', views.readingpage, name='readingpage'),
    path('get_session/', views.get_session, name='get_session'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('cancel_subscription/', views.cancel_subscription, name='cancel_subscription'),
]
