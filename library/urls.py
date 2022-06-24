from django.urls import path
from library import views

urlpatterns = [
    path('', views.guest_view, name="guest"),
    path('login/', views.userlogin_view, name="userlogin"),
    path('create-user/', views.usercreate_view, name="usercreate"),
    path('select-library/', views.libraryselect_view, name="libraryselect"),
    path('create-library/', views.librarycreate_view, name="librarycreate"),
    path('profile/', views.profile_view, name="profile"),
    path('library/', views.library_view, name="library"),
    path('logout/', views.logout_view, name="logout"),
]