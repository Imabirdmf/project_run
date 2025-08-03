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
    athlete = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.CharField(max_length=200)
    status = models.CharField(max_length=200, choices=STATUS_CHOCES, default='init')