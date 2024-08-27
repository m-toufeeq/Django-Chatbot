from django.db import models
from django.contrib.auth.models import User 


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    period_start_date = models.DateField(auto_now_add=True)



class SymptomLog(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    symptom = models.CharField(max_length=100)
    log_date = models.DateField(auto_now_add=True)
    cycle_day = models.IntegerField()

class Flow(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

class FlowStep(models.Model):
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE)
    step_number = models.IntegerField()
    text = models.TextField()
    is_final_step = models.BooleanField(default=False)

class FlowOption(models.Model):
    step = models.ForeignKey(FlowStep, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=100)
    next_step = models.ForeignKey(FlowStep, null=True, blank=True, on_delete=models.SET_NULL, related_name='previous_options')

class UserResponse(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    step = models.ForeignKey(FlowStep, on_delete=models.CASCADE)
    response = models.CharField(max_length=100)
    response_date = models.DateTimeField(auto_now_add=True)

