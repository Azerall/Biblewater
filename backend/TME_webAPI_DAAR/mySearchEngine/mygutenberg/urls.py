from django.urls import path
from mygutenberg import views

urlpatterns = [
    path('books/', views.BooksList.as_view()),
    path('book/<int:pk>/', views.BookDetail.as_view()),
    path('frenchbooks/', views.FrenchBooksList.as_view()),
    path('frenchbook/<int:pk>/', views.FrenchBookDetail.as_view()),
    path('englishbooks/', views.EnglishBooksList.as_view()),
    path('englishbook/<int:pk>/', views.EnglishBookDetail.as_view()),
    path('book/<int:book_id>/coverImage/', views.BookCoverImage.as_view()),
    path('book/<int:book_id>/image/', views.BookRandomImage.as_view()),
    path('book/<int:book_id>/image/<int:image_id>/', views.BookSpecificImage.as_view()),

    path('search/<str:keyword>/', views.SearchByKeyword.as_view()),
    path('regex/<str:regex>/', views.SearchByRegex.as_view()),
    path('search_with_suggestions/<str:keyword>/', views.SearchWithSuggestions.as_view()),
]