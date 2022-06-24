from django.urls import path
from members import views

urlpatterns = [
    path('', views.members_view, name='members'),
    path('add/', views.memberscreate_view, name='memberscreate'),
    path('edit/<int:id>', views.membersedit_view, name='membersedit'),
    path('delete/<int:id>', views.membersdelete_view, name='membersdelete'),
    path('details/<int:id>', views.membersdetail_view, name='membersdetail'),
]