from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Run(models.Model):
    STATUS_CHOCES = {
        'init': 'init',
        'in_progress': 'in_progress',
        'finished': 'finished'
    }
    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='runs')
    comment = models.CharField(max_length=200)
    status = models.CharField(max_length=200, choices=STATUS_CHOCES, default='init')
    distance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)



class AthleteInfo(models.Model):
    goals = models.CharField(max_length=200, null=True)
    weight = models.IntegerField(null=True)
    user_id = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )


class Challenge(models.Model):
    full_name = models.CharField(max_length=200)
    athlete = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='challenges')


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, null=False, related_name='positions')
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
