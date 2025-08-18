from django.http import QueryDict
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from .models import Run, AthleteInfo, Challenge, Position
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .serializers import RunSerializer, StaffSerializer, ChallengeSerializer, PositionSerializer
from geopy import distance


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
            positions = run.positions.all()
            start_position = (positions.first().latitude, positions.first().longitude)
            run_distance = float(run.distance)
            for pos in positions:
                stop_position = (pos.latitude, pos.longitude)
                run_distance += distance.distance(start_position, stop_position).km
                start_position = stop_position
            run.distance = run_distance
            run.save()
            if run.athlete.runs.filter(status='finished').count() == 10:
                Challenge.objects.update_or_create(
                    full_name = 'Сделай 10 Забегов!',
                    athlete = run.athlete
                )
            return Response(data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class AthleteView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        athlete, created = AthleteInfo.objects.update_or_create(
            user_id = user
        )
        return Response(data={
            'goals': athlete.goals,
            'weight' : athlete.weight,
            'user_id': user.id
        })

    def put(self, request, user_id):
        goals = request.data.get('goals')
        weight = request.data.get('weight')
        user = get_object_or_404(User, id=user_id)
        if weight.isdigit() and 0 < int(weight) < 900:
            AthleteInfo.objects.update_or_create(
                user_id=user,
                defaults={
                    'goals': goals,
                    'weight': int(weight)
                }
            )
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ChallengesViewSet(viewsets.ModelViewSet):
    serializer_class = ChallengeSerializer
    queryset = Challenge.objects.all()

    def get_queryset(self):
        qs = User.objects.filter(is_superuser=False)
        user_id = self.request.query_params.get('athlete', None)
        if user_id:
            qs = get_object_or_404(User, id=user_id)
            qs = qs.challenges.all()
        return qs


class PositionViewSet(viewsets.ModelViewSet):
    serializer_class = PositionSerializer
    queryset = Position.objects.all().select_related('run')

    def get_queryset(self):
        qs = Position.objects.all()
        run_id = self.request.query_params.get('run', None)
        if run_id:
            run_obj = get_object_or_404(Run, id=run_id)
            qs = Position.objects.filter(run=run_obj)
        return qs