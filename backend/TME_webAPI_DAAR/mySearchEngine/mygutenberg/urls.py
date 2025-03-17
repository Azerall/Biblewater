from django.urls import path
from mygutenberg import views

urlpatterns = [
    path('books/', views.BooksList.as_view()),
    path('book/<int:pk>/', views.BookDetail.as_view()),
    path('book/<int:book_id>/coverImage/', views.BookCoverImage.as_view()),
    path('frenchbooks/', views.FrenchBooksList.as_view()),
    path('englishbooks/', views.EnglishBooksList.as_view()),
    path('search/<str:keyword>/', views.SearchByKeyword.as_view()),
    path('regex/<str:regex>/', views.SearchByRegex.as_view()),
    path('search_with_ranking/<str:keyword>/<str:ranking>/', views.SearchWithRanking.as_view()),
    path('search_with_suggestions/<str:keyword>/', views.SearchWithSuggestions.as_view()),
]