from rest_framework import serializers
from blackrot.models import Blackrot, Daily, Data, State #, LANGUAGE_CHOICES, STYLE_CHOICES 

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        #fields = ['LotId', 'year','doy','cumulateInfection','cumulateInfectionBerry']
        fields = '__all__'
class DailyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Daily
        fields = ['hod', 'temperature', 'humidity','leafwetness','rain','GS','treatment']

class DataListSerializer(serializers.ModelSerializer):
    data_daily=DailyListSerializer(many=True)
    class Meta:
        model = Data
        fields = ['LotId', 'year','doy','data_daily']
        
    def create(self, validated_data): #questa serve per i nested dictionaries (https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers)
        data_daily_data = validated_data.pop('data_daily')
        blackrot_daily = Data.objects.create(**validated_data)
        for i in data_daily_data:
            Daily.objects.create(blackrot_daily=blackrot_daily, **i)
        return blackrot_daily

        
class BlackrotListSerializer(serializers.ModelSerializer):
    
       data=DataListSerializer(many=True)
       #state=StateSerializer(many=True,required=False)
       state=StateSerializer(required=False)
       class Meta:
           model = Blackrot
          # fields = ['id','data','state']
           fields = '__all__'
           #depth=2 #https://testdriven.io/blog/drf-serializers/

       def create(self, validated_data): #questa serve per i nested dictionaries (https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers)
            data_data = validated_data.pop('data')
            blackrot_data = Blackrot.objects.create(**validated_data)
            for i in data_data:
                Data.objects.create(blackrot_data=blackrot_data, **i)
                  
                data_state = validated_data.pop('state')
                blackrot_state = Blackrot.objects.create(**validated_data)
                for i in data_state:
                    State.objects.create(blackrot_state=blackrot_state, **i)
                      
            return blackrot_data, blackrot_state
               