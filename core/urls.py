from django.urls import path
from .views import BookingWizard, booking_success
from .forms import BusinessForm, GuestForm, BookingForm

urlpatterns = [
    path("reserva/", BookingWizard.as_view([GuestForm,BusinessForm, BookingForm]), name="booking_step"),
    path("reserva/sucesso/", booking_success, name="booking_success"),
]