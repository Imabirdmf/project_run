from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from .models import Run
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .serializers import RunSerializer, StaffSerializer


class Pagination(PageNumberPagination):
    # page_size = 5
    page_size_query_param = 'size'
    max_page_size = 50


@api_view(['GET'])
def company_details(request):
    details = {'company_name': settings.COMPANY_NAME,
                'slogan': settings.SLOGAN,
                'contacts': settings.CONTACTS }
    return Response(details)


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['athlete', 'status']
    ordering_fields = ['created_at']


class StaffViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StaffSerializer
    queryset = User.objects.all()
    pagination_class = Pagination
    filter_backends = [SearchFilter, OrderingFilter]  # Подключаем SearchFilter здесь
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']

    def get_queryset(self):
        qs = User.objects.filter(is_superuser=False)
        type_staff = self.request.query_params.get('type', None)
        if type_staff == 'coach':
            qs = qs.filter(is_staff=True)
        elif type_staff == 'athlete':
            qs = qs.filter(is_staff=False)
        return qs


class StartRunView(APIView):
    def post(self, request, id):
        run = get_object_or_404(Run, id=id)
        current_status = run.status
        data = {"message": "POST запрос обработан"}
        if current_status == 'init':
            run.status = run.STATUS_CHOCES.get('in_progress')
            run.save()
            return Response(data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class StopRunView(APIView):
    def post(self, request, id):
        data = {"message": "POST запрос обработан"}
        run = get_object_or_404(Run, id=id)
        current_status = run.status
        if current_status == 'in_progress':
            run.status = run.STATUS_CHOCES.get('finished')
            run.save()
            return Response(data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)