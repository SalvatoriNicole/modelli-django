#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 18:32:04 2024

@author: nicole
"""

from rest_framework import serializers
from pseudoperonospora.models import Pseudoperonospora, Daily, Data, State #, LANGUAGE_CHOICES, STYLE_CHOICES 

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        #fields = ['LotId', 'year','doy','cumulateInfection','cumulateInfectionBerry']
        fields = '__all__'
class DailyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Daily
        fields = ['hod', 'temperature', 'leafwetness']
  
#### questo da controllare    
  
    
class DataListSerializer(serializers.ModelSerializer):
    data_daily=DailyListSerializer(many=True)
    class Meta:
        model = Data
        fields = ['LotId', 'year','doy','data_daily']
        
    def create(self, validated_data): #questa serve per i nested dictionaries (https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers)
        data_daily_data = validated_data.pop('data_daily')
        pseudoperonospora_daily = Data.objects.create(**validated_data)
        for i in data_daily_data:
            Daily.objects.create(pseudoperonospora_daily=pseudoperonospora_daily, **i)
        return pseudoperonospora_daily

        
class PseudoperonosporaListSerializer(serializers.ModelSerializer):
    
       data=DataListSerializer(many=True)
       state=StateSerializer(required=False)
       class Meta:
           model = Pseudoperonospora
          # fields = ['id','data','state']
           fields = '__all__'
           #depth=2 #https://testdriven.io/blog/drf-serializers/

       def create(self, validated_data): #questa serve per i nested dictionaries (https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers)
            data_data = validated_data.pop('data')
            pseudoperonospora_data = Pseudoperonospora.objects.create(**validated_data)
            for i in data_data:
                Data.objects.create(pseudoperonospora_data=pseudoperonospora_data, **i)
                  
                data_state = validated_data.pop('state')
                pseudoperonospora_state = Pseudoperonospora.objects.create(**validated_data)
                for i in data_state:
                    State.objects.create(pseudoperonospora_state=pseudoperonospora_state, **i)
                      
            return pseudoperonospora_data, pseudoperonospora_state
               
