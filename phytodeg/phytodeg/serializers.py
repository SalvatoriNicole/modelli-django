from rest_framework import serializers
from phytodeg.models import PhytoDeg, LANGUAGE_CHOICES, STYLE_CHOICES 

class PhytoDegListSerializer(serializers.Serializer):

   # tc = serializers.IntegerField(required=False)
   # tf = serializers.IntegerField(required=False) 
   # k = serializers.FloatField(required=False)
   # lambdav = serializers.FloatField(required=False)

    
    A1 = serializers.FloatField(required=False)
    mu1 = serializers.FloatField(required=False) 
    sigma1 = serializers.FloatField(required=False)
    A2 = serializers.FloatField(required=False)
    mu2 = serializers.FloatField(required=False) 
    sigma2 = serializers.FloatField(required=False)
    C = serializers.FloatField(required=False) 
    D = serializers.FloatField(required=False)


    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return PhytoDeg.objects.create(**validated_data)

