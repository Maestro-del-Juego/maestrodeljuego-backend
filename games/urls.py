"""games URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('api-auth/', include('rest_framework.urls')),
    path('library/', views.LibraryView.as_view(), name='user-library'),
    path('games/<int:bgg>/', views.GameDetailView.as_view(), name='game-detail'),
    path('wishlist/', views.WishListView.as_view(), name='user-wishlist'),
    path('gamenight/', views.GameNightView.as_view(), name='game-night'),
    path('gamenight/<str:rid>/', views.GameNightDetailView.as_view(), name='game-night-detail'),
    path('gamenight/<str:rid>/voting/', views.VotingView.as_view(), name='game-night-votes'),
    path('gamenight/<str:rid>/feedback/', views.GeneralFeedbackView.as_view(), name='game-night-feedback'),
    path('gamenight/<str:rid>/gamefeedback/', views.GameFeedbackView.as_view(), name='indiv-game-feedback'),
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    path('contacts/', views.ContactListView.as_view(), name='contact-list'),
    path('contacts/<int:pk>/', views.ContactUpdateView.as_view(), name='contact-update'),
    path('gamenight/<str:rid>/RSVP/', views.RSVPListCreateView.as_view(), name='game-night-RSVP'),
]