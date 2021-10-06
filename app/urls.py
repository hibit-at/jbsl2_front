from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('user/',views.user,name='user'),
    path('what/',views.what,name='what'),
    path('leaderboard/',views.leaderboard,name='leaderboard'),
    path('mapboard/',views.mapboard,name='mapboard'),
    path('submission/',views.submission,name='submission'),
    path('register/',views.register,name='register'),
]