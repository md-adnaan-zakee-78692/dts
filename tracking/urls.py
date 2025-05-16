from django.urls import path
from .views import DocumentCreateView, DocumentListView, DocumentActionView, DashboardView

urlpatterns = [
    path('create/', DocumentCreateView.as_view(), name='document-create'),
    path('', DocumentListView.as_view(), name='document-list'),
    path('<int:pk>/action/', DocumentActionView.as_view(), name='document-action'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    



    # path('mydocuments/', views.MyDocumentsView.as_view(), name='mydocuments'),





]
