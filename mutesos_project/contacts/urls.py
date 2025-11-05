from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.manage_contacts, name='manage_contacts'),
    path('toggle/<int:pk>/', views.toggle_contact_active, name='toggle_contact_active'),
    path('delete/<int:pk>/', views.delete_contact, name='delete_contact'),

    path('helplines/', views.manage_helplines, name='manage_helplines'),
    path('helplines/toggle/<int:pk>/', views.toggle_helpline_active, name='toggle_helpline_active'),
    path('helplines/delete/<int:pk>/', views.delete_helpline, name='delete_helpline'),
]


