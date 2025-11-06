# core/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DeveloperViewSet, CommitViewSet, JiraTicketViewSet, ChatDataViewSet, BurnoutRiskView, ProductivityScoreView, CollaborationScoreView

router = DefaultRouter()
router.register(r'developers', DeveloperViewSet)
router.register(r'commits', CommitViewSet)
router.register(r'tickets', JiraTicketViewSet)
router.register(r'chat', ChatDataViewSet)

urlpatterns = router.urls

# Add the specific path for the Burnout Risk API endpoint
urlpatterns += [
    path('burnout/<int:pk>/', BurnoutRiskView.as_view(), name='burnout-risk'),
    path('productivity/<int:pk>/', ProductivityScoreView.as_view(), name='productivity-score'),
    path('collaboration/<int:pk>/', CollaborationScoreView.as_view(), name='collaboration-score'),
]