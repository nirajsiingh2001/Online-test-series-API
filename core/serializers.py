from rest_framework import serializers
from .models import Test, UserProfile,TestSeries,Question

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields='__all__'

class TestSeriesSerializer(serializers.ModelSerializer):
    created_by=serializers.CharField(source='created_by.username',read_only=True)
    class Meta:
        model=TestSeries
        fields='__all__'
        extra_kwargs={
            'created_by':{'read_only':True}
        }

class TestSerializer(serializers.ModelSerializer):
    created_by=serializers.CharField(source='created_by.username',read_only=True)
    class Meta:
        model=Test
        fields='__all__'
        extra_kwargs={
            'created_by':{'read_only':True}
        }

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields='__all__'

    def to_representation(self, instance):
        data=super().to_representation(instance)
        user=self.context.get('request').user

        if user.userprofile.role=='student':
            data.pop('correct_option',None)
        return data