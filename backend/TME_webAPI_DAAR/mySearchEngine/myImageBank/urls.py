from django.urls import path
from myImageBank import views

urlpatterns = [
    path('random/', views.RandomImage.as_view()),
    path('<int:image_id>/', views.Image.as_view()),
    path('myImageFromString/<str:newName>/', views.ImageFromString.as_view()),
]