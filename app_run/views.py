from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from django.conf import settings
from rest_framework import viewsets
from .models import Run
from django.contrib.auth.models import User
from .serializers import RunSerializer, StaffSerializer


@api_view(['GET'])
def company_details(request):
    details = {'company_name': settings.COMPANY_NAME,
                'slogan': settings.SLOGAN,
                'contacts': settings.CONTACTS }
    return Response(details)


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer


class StaffViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StaffSerializer
    queryset = User.objects.all()
    filter_backends = [SearchFilter]  # Подключаем SearchFilter здесь
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        qs = User.objects.filter(is_superuser=False)
        type_staff = self.request.query_params.get('type', None)
        if type_staff == 'coach':
            qs = qs.filter(is_staff=True)
        elif type_staff == 'athlete':
            qs = qs.filter(is_staff=False)
        return qs

