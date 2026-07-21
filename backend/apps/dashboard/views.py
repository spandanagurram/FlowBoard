from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import DashboardSummarySerializer
from .services import DashboardService


class DashboardSummaryAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DashboardSummarySerializer

    def get(self, request):
        summary = DashboardService.get_dashboard_summary(request.user)
        serializer = self.get_serializer(summary)
        return Response(serializer.data)
