from django.urls import path
from books import views

urlpatterns = [
    path('', views.books_view, name='books'),
    path('details/<int:id>', views.booksdetail_view, name='bookdetail'),
    path('edit/<int:id>', views.bookedit_view, name='bookedit'),
    path('add/', views.bookadd_view, name='bookadd'),
    path('delete/<int:id>', views.bookdelete_view, name='bookdelete'),
]