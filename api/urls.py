from django.urls import path, include
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r'tickets', views.TicketViewSet, basename="tickets")
router.register(r'users', views.UserViewSet)
router.register(r'auth', views.AuthView, basename="auth")
router.register(r'tickets/(?P<ticket_id>\d+)/image', views.ImagesViewSet, basename="images")

urlpatterns = [
    path('', include(router.urls))
]