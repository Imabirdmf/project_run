from rest_framework import serializers
from .models import Run, Challenge, Position
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name', 'athleteinfo']


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserSerializer(source='athlete', read_only=True)
    class Meta:
        model = Run
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished']

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

    def get_runs_finished(self, obj):
        return obj.runs.all().filter(status='finished').count()


class ChallengeSerializer(serializers.ModelSerializer):
    # athlete_data = UserSerializer(source='athlete', read_only=True)
    class Meta:
        model = Challenge
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

    def validate_latitude(self, value):
        if -90.0 <= value <= 90.0:
            return value
        raise serializers.ValidationError

    def validate_longitude(self, value):
        if -180.0 <= value <= 180.0:
            return value
        raise serializers.ValidationError

    def validate_run(self, value):
        print(value)
        value = get_object_or_404(Run, id=value.id)
        if value.status == 'in_progress':
            return value
        raise serializers.ValidationError

