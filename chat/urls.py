from django.urls import path

from . import views

from .tasks import StartupTasks

StartupTasks.run_only_in_server()

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:room_name>/', views.room, name='room'),
]
