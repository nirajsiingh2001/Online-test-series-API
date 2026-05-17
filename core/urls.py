from django.urls import path
from .views import (UserProfileAPIView,UserRegisterAPIView,
                    LoginAPIView,TestSeriesAPIView,
                    TestAPIView,QuestionAPIView,
                    SubmitTestAPIView,ResultAPIView,VerifyEmailAPIView
                    
                    )

urlpatterns=[
    path('profile/',UserProfileAPIView.as_view()),
    path('register/',UserRegisterAPIView.as_view()),
    path('verify-email/<uuid:token>/',VerifyEmailAPIView.as_view()),
    path('login/',LoginAPIView.as_view()),
    path('test-series/',TestSeriesAPIView.as_view()),
    path('test/',TestAPIView.as_view()),
    path('question/',QuestionAPIView.as_view()),
    path('submit-test/',SubmitTestAPIView.as_view()),
    path('result/<int:result_id>/',ResultAPIView.as_view()),

]