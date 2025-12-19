from rest_framework import serializers
from chooseplants.models import Chooseplants, Data#, LANGUAGE_CHOICES, STYLE_CHOICES 

    
class DataListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = ['LotId', 'year','month','location','semina']
        
class ChooseplantsListSerializer(serializers.ModelSerializer):
    
       data=DataListSerializer(many=True)

       class Meta:
           model = Chooseplants
          # fields = ['id','data','state']
           fields = '__all__'
           #depth=2 #https://testdriven.io/blog/drf-serializers/

       def create(self, validated_data): #questa serve per i nested dictionaries (https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers)
            data_data = validated_data.pop('data')
            chooseplants_data = Chooseplants.objects.create(**validated_data)
            for i in data_data:
                Data.objects.create(chooseplants_data=chooseplants_data, **i)
                                       
            return chooseplants_data
               
