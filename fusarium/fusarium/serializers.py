#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 18:32:04 2024

@author: nicole
"""

from rest_framework import serializers
from fusarium.models import Fusarium, Daily, Data, State #, LANGUAGE_CHOICES, STYLE_CHOICES 

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'
class DailyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Daily
        fields = ['hod', 'temperature', 'leafwetness','rain','humidity','GS']
  
#### questo da controllare    
  
    
class DataListSerializer(serializers.ModelSerializer):
    data_daily=DailyListSerializer(many=True)
    class Meta:
        model = Data
        fields = ['LotId', 'year','doy','data_daily']
        
    def create(self, validated_data): #questa serve per i nested dictionaries (https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers)
        data_daily_data = validated_data.pop('data_daily')
        fusarium_daily = Data.objects.create(**validated_data)
        for i in data_daily_data:
            Daily.objects.create(fusarium_daily=fusarium_daily, **i)
        return fusarium_daily

        
class FusariumListSerializer(serializers.ModelSerializer):
    
       data=DataListSerializer(many=True)
       state=StateSerializer(required=False)
       class Meta:
           model = Fusarium
          # fields = ['id','data','state']
           fields = '__all__'
           #depth=2 #https://testdriven.io/blog/drf-serializers/

       def create(self, validated_data): #questa serve per i nested dictionaries (https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers)
            data_data = validated_data.pop('data')
            fusarium_data = Fusarium.objects.create(**validated_data)
            for i in data_data:
                Data.objects.create(fusarium_data=fusarium_data, **i)
                  
                data_state = validated_data.pop('state')
                fusarium_state = Fusarium.objects.create(**validated_data)
                for i in data_state:
                    State.objects.create(fusarium_state=fusarium_state, **i)
                      
            return fusarium_data, fusarium_state
               
