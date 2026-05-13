from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student','Student'),
    )
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    full_name=models.CharField(max_length=50)
    phone=models.CharField(max_length=20)
    role=models.CharField(max_length=20,choices=ROLE_CHOICES,default='student')
    profile_image=models.ImageField(upload_to='profiles/',null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class TestSeries(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField()
    price=models.DecimalField(max_digits=8,decimal_places=2)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Test(models.Model):
    test_series=models.ForeignKey(TestSeries,on_delete=models.CASCADE)
    title=models.CharField(max_length=100)
    duration=models.IntegerField(help_text="Duration in minutes")
    total_marks=models.IntegerField()
    created_by=models.ForeignKey(User,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True)
    def __str__(self):
        return self.title
    
class Question(models.Model):
    test=models.ForeignKey(Test,on_delete=models.CASCADE)
    question=models.TextField()
    option_a=models.CharField(max_length=100)
    option_b=models.CharField(max_length=100)
    option_c=models.CharField(max_length=100)
    option_d=models.CharField(max_length=100)

    correct_option=models.CharField(max_length=1)
    marks=models.IntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.question
    
class Result(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    test=models.ForeignKey(Test,on_delete=models.CASCADE)
    score=models.IntegerField(default=0)
    total_marks=models.IntegerField()
    percentage=models.FloatField()
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.test.title}"
    
class UserAnswer(models.Model):
    result=models.ForeignKey(Result,on_delete=models.CASCADE)
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    selected_option=models.CharField(max_length=1)
    is_correct=models.BooleanField()
    def __str__(self):
        return f"{self.question.id} - {self.selected_option}"
  