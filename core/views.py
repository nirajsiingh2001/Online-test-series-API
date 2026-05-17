from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404


from .models import UserProfile,TestSeries,Test,Question,Result,UserAnswer
from .serializers import UserProfileSerializer,TestSeriesSerializer,TestSerializer,QuestionSerializer

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get (self, request):
        print("Get profile API called")
        profile=UserProfile.objects.get(user=request.user)
        print("Profile found:", profile)
        serializer=UserProfileSerializer(profile)
        return Response(serializer.data)
    
    def post(self,request):
        print("post profile api called")
        print("Request data:", request.data)

        profile, created=UserProfile.objects.get_or_create(user=request.user)
        serializer=UserProfileSerializer(profile,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            if created:
                return Response({
                    "message": "Profile created successfully",
                    "data": serializer.data
                },status=status.HTTP_201_CREATED)
            return Response({
                "message":"profile updated successfully","data":serializer.data
            },status=status.HTTP_200_OK)
    
        return Response(
            serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class UserRegisterAPIView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        username=request.data.get("username")
        password=request.data.get("password")
        email=request.data.get("email")
        full_name=request.data.get("full_name")
        phone=request.data.get("phone")
        role=request.data.get("role")
        print("username",username)
        if User.objects.filter(username=username).exists():
            return Response({"error":"Username already exists"},status=status.HTTP_400_BAD_REQUEST)
        user=User.objects.create_user(username=username,password=password,email=email)
        #
        profile =UserProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            role=role
        )
        verification_link=request.build_absolute_uri(
            f"/api/verify-email/{profile.email_verification_token}/"
        )
        print("Verification link generated:", verification_link)
        print("Sending verification email to:", user.email)
        print("Email content:", f"Hello {user.username},\n\nPlease verify your email by clicking the following link:\n{verification_link}\n\nThank you!")
        send_mail(
            subject="Email verification",
            message=(f"Hello {user.username},\n\n"
                    f"Thank you for registering on our platform.\n"
                    f"Please click the link below to verify your email address:\n"
                    f"{verification_link}\n\n"
                    f"Thank you,"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
        )
        print("Verification email sent to:", user.email)
        print("Verification link:", verification_link)
        print("User created:", user)
        print("User profile created:", profile)
        return Response({"message":"User registered successfully. Please check your email to verify your account."},status=status.HTTP_201_CREATED)

class VerifyEmailAPIView(APIView):
    permission_classes=[AllowAny]
    def get(self,request,token):
        print("Email verification API called")
        print("Token received:", token)
        profile=get_object_or_404(UserProfile,email_verification_token=token)
        print("Profile found for token:", profile)
        profile.is_email_verified=True
        profile.email_verification_token=None
        profile.save()
        print("Email verified for user:", profile.user.username)
        return Response({"message":"Email verified successfully. You can now log in."},status=status.HTTP_200_OK)

        
    
    

class LoginAPIView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        username=request.data.get("username")
        password=request.data.get("password")
        user=authenticate(username=username,password=password)   

        if user is None:
            return Response({"error":"Invalid credentials"},status=status.HTTP_400_BAD_REQUEST)
        profile=user.userprofile
        if not profile.is_email_verified:
            return Response({"error":"Email not verified. Please check your email."},status=status.HTTP_400_BAD_REQUEST)
        
        token,created=Token.objects.get_or_create(user=user)
        print(token.key)
        send_mail(
            subject="login alert",
            message=f"hello{user.username},you have successfully logged in.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,

        )
        return Response({"message":"Login successful","token":token.key},status=status.HTTP_200_OK)

class TestSeriesAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        test_series=TestSeries.objects.filter(is_active=True)
        print("Test series found:", test_series)
        serializer=TestSeriesSerializer(test_series,many=True)
        print(serializer.data)
        return Response(serializer.data)
    
    def post(self,request):
        print("post test series api called")
        print("Request data:", request.data)
        profile=request.user.userprofile
        if profile.role!="admin":
            return Response({"message":"only admin can create test series"},status=403)
        serializer=TestSeriesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response({"message":"Test series created successfully","data":serializer.data},status=status.HTTP_201_CREATED)
        
        print(serializer.errors)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class TestAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        tests=Test.objects.filter(is_active=True)
        serializer=TestSerializer(tests,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        print("post test api called")
        print("Request data:", request.data)
        profile=request.user.userprofile
        print("User profile:", profile)
        if profile.role!="admin":
            return Response({"message":"only admin can create test"},status=status.HTTP_403_FORBIDDEN)
        serializer=TestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response({"message":"Test created successfully","data":serializer.data},status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST
     )
    
class QuestionAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        print("Get questions API called")
        test_id=request.query_params.get("test")
        if not test_id:
            return Response({"error":"Test id is required"},status=status.HTTP_400_BAD_REQUEST)
        else:
            question=Question.objects.filter(test=test_id)
            print("Questions found:", question)
            serializer=QuestionSerializer(question,many=True,context={'request':request})
            print(serializer.data)
            return Response(serializer.data)
        
    def post(self,request):
        print("post question api called")
        print("Request data:", request.data)
        profile=request.user.userprofile
        if profile.role!="admin":
            return Response({"message":"only admin can create question"},status=status.HTTP_403_FORBIDDEN)
        if isinstance(request.data,list):
            serializer=QuestionSerializer(data=request.data,many=True,context={'request':request})
        else:
            print("Bulk question creation detected")
            serializer=QuestionSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Question(s) created successfully","data":serializer.data},status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
     
class SubmitTestAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        print("Submit test API called")
        print("Request data:", request.data)
        user=request.user
        test_id=request.data.get("test")
        answers=request.data.get("answers",[])
        print("User:", user)
        print("Test ID:", test_id)
        print("Answers:", answers)

        try:
            test=Test.objects.get(id=test_id)
        except Test.DoesNotExist:
                return Response({"error":"Test not found"},status=status.HTTP_404_NOT_FOUND)
        
        #(BEFORE Result.objects.create)
        existing_result=Result.objects.filter(user=user,test=test).first()
        if existing_result:
            return Response({"error":"you have already sumbitted this test"},status=400)
        
        # Create result entry for the user and test
        result=Result.objects.create(user=user,
                                     test=test,
                                     score=0,
                                     total_marks=0,
                                     percentage=0
                                     )
        print("Result created:", result)
        #m prepare variables to calculate score and total marks
        total_marks=0
        score=0
        #loop through answers and calculate score and total marks
        for ans in answers:
            question_id=ans.get("question")
            selected_option=ans.get("selected_option")
            #Fetch question from database
            try:
                question=Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                continue
            #Add total marks
            total_marks+=question.marks
            # check correctness of answer and calculate score
            is_correct=(selected_option==question.correct_option)
            if is_correct:
                score+=question.marks
            print(f"Question ID: {question_id}, Selected Option: {selected_option}, Correct Option: {question.correct_option}, Is Correct: {is_correct}, Score: {score}, Total Marks: {total_marks}")
            #Save user answer
            UserAnswer.objects.create(
                result=result,
                question=question,
                selected_option=selected_option,
                is_correct=is_correct
            )
            print("User answer saved")
        #Calculate percentage
        if total_marks>0:
            percentage=(score/total_marks)*100
        else:
            percentage=0
        #Update result with score,total marks and percentage
        result.score=score
        result.total_marks=total_marks
        result.percentage=percentage
        result.save()
        print("Result updated:", result)

        return Response({"message":"Test sumbitted successfully","score":score,"total_marks":total_marks,"percentage":percentage},status=status.HTTP_200_OK )
    
class ResultAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,result_id):
        print("Get result API called")
        user=request.user
        print("User:", user)
        try:
            result=Result.objects.get(id=result_id,user=user)
            print("Result found:", result)
        except Result.DoesNotExist:
            return Response({"error":"result not found"},status=400)
        answers=UserAnswer.objects.filter(result=result)
        print("User answers found:", answers)
        data=[]
        print("Preparing response data")
        for ans in answers:
            question=ans.question
            data.append({
                "question":question.question,
                "option_a":question.option_a,
                "option_b":question.option_b,
                "option_c":question.option_c,
                "option_d":question.option_d,
                "correct_option":question.correct_option,
                "your_answer":ans.selected_option,
                "is_correct":ans.is_correct,
                "marks":question.marks
            })
        print("Response data prepared:", data)
        return Response({
            "test":result.test.title,
            "score":result.score,
            "total_marks":result.total_marks,
            "percentage":result.percentage,
            "answers":data
        })

class VerifyEmailAPIView(APIView):
    permission_classes=[AllowAny]
    def get(self,request,token):
        print("Email verification API called")
        print("Token received:", token)
        try:
            profile=UserProfile.objects.get(email_verification_token=token)
            print("Profile found for token:", profile)
        except UserProfile.DoesNotExist:
            return Response({"error":"Invalid token"},status=status.HTTP_400_BAD_REQUEST)
        profile.is_email_verified=True
        profile.email_verification_token=None
        profile.save()
        print("Email verified for user:", profile.user.username)
        return Response({"message":"Email verified successfully. You can now log in."},status=status.HTTP_200_OK)