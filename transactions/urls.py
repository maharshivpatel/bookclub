from django.urls import path
from transactions import views

urlpatterns = [
    path('', views.transactions_view, name='transactions'),
    path('details/<int:id>', views.transactiondetail_view, name='transactiondetail'),
    path('addmoney/', views.moneyadd_view, name='moneyadd'),
    path('issue/', views.bookissue_view, name='bookissue'),
    path('return/<int:id>', views.bookreturn_view, name='bookreturn'),
    path('lost/<int:id>', views.booklost_view, name='booklost'),
    path('delete/<int:id>', views.transactiondelete_view, name='transactiondelete'),
]