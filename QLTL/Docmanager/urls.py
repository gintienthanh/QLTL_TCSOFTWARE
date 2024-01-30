from django.urls import path
from . import views

urlpatterns = [
    path('boxcase/',views.BoxCaseView.as_view(),name='view_boxcase'),
]
