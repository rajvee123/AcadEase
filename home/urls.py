from django.contrib import admin
from django.urls import path, include
from home import views


from django.urls import path
from home import views  # Import views from home app

urlpatterns = [
    path("", views.index, name="home"),  # Homepage
]
from django.urls import path
from home import views

urlpatterns = [
    path("", views.index, name="home"),
]
from django.urls import path
from home import views

urlpatterns = [
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("courses/", views.courses, name="courses"),
    path("team/", views.team, name="team"),
    path("testimonial/", views.testimonial, name="testimonial"),
]
from django.urls import path
from home import views  # Import views from home app

urlpatterns = [
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("courses/", views.courses, name="courses"),
    path("team/", views.team, name="team"),
    path("testimonial/", views.testimonial, name="testimonial"),
]

