# Create your views here.
# core/views.py
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Developer, Commit, JiraTicket, ChatData
from .serializers import DeveloperSerializer, CommitSerializer, JiraTicketSerializer, ChatDataSerializer
from .ml_services import get_burnout_risk, calculate_single_developer_features, get_productivity_score, calculate_productivity_features, get_collaboration_score, calculate_collaboration_features

class DeveloperViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Developers to be viewed or edited.
    """
    queryset = Developer.objects.all().order_by('name')
    serializer_class = DeveloperSerializer

class CommitViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Commits to be viewed or edited.
    """
    queryset = Commit.objects.all().order_by('-timestamp')
    serializer_class = CommitSerializer


class JiraTicketViewSet(viewsets.ModelViewSet):
    queryset = JiraTicket.objects.all().order_by('-created_at')
    serializer_class = JiraTicketSerializer


class ChatDataViewSet(viewsets.ModelViewSet):
    queryset = ChatData.objects.all().order_by('-timestamp')
    serializer_class = ChatDataSerializer


class BurnoutRiskView(APIView):
    """
    API endpoint that dynamically calculates features and gets the ML prediction.
    URL: /api/v1/burnout/<int:pk>/
    """
    def get(self, request, pk, format=None):
        
        # 1. DYNAMICALLY AGGREGATE THE REAL FEATURES FOR THE GIVEN DEVELOPER (pk)
        developer_features = calculate_single_developer_features(pk)
        
        if developer_features is None:
            return Response({'error': f'Developer with ID {pk} not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # 2. Get the prediction
        result, status_code = get_burnout_risk(developer_features)

        if status_code != 200:
            return Response(result, status=status_code)
        
        # Add the features back into the response for transparency (optional)
        result['features'] = developer_features
        
        return Response(result, status=status.HTTP_200_OK)


class ProductivityScoreView(APIView):
    """
    API endpoint to get the productivity score for a specific developer.
    URL: /api/v1/productivity/<int:pk>/
    """
    def get(self, request, pk, format=None):
        developer_features = calculate_productivity_features(pk)

        if developer_features is None:
             return Response({'error': f'Developer with ID {pk} not found.'}, status=status.HTTP_404_NOT_FOUND)

        result, status_code = get_productivity_score(developer_features)

        if status_code != 200:
            return Response(result, status=status_code)

        result['features'] = developer_features
        return Response(result, status=status.HTTP_200_OK)


class CollaborationScoreView(APIView):
    """
    API endpoint to get the collaboration score for a specific developer.
    URL: /api/v1/collaboration/<int:pk>/
    """
    def get(self, request, pk, format=None):
        developer_features = calculate_collaboration_features(pk)

        if developer_features is None:
             return Response({'error': f'Developer with ID {pk} not found.'}, status=status.HTTP_404_NOT_FOUND)

        result, status_code = get_collaboration_score(developer_features)

        if status_code != 200:
            return Response(result, status=status_code)

        result['features'] = developer_features
        return Response(result, status=status.HTTP_200_OK)