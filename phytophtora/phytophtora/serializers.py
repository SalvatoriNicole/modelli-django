#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 16:43:21 2024

@author: nicole
"""

from rest_framework import serializers
from phytophtora.models import Phytophtora, Daily, Data, State #, LANGUAGE_CHOICES, STYLE_CHOICES 

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        #fields = ['LotId', 'year','doy','hours_of_wetness_t0','hours_of_dry_t0']
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
        phytophtora_daily = Data.objects.create(**validated_data)
        for i in data_daily_data:
            Daily.objects.create(phytophtora_daily=phytophtora_daily, **i)
        return phytophtora_daily

        
class PhytophtoraListSerializer(serializers.ModelSerializer):
    
       data=DataListSerializer(many=True)
       #state=StateSerializer(many=True,required=False)
       state=StateSerializer(required=False)
       class Meta:
           model = Phytophtora
          # fields = ['id','data','state']
           fields = '__all__'
           #depth=2 #https://testdriven.io/blog/drf-serializers/

       def create(self, validated_data): #questa serve per i nested dictionaries (https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers)
            data_data = validated_data.pop('data')
            phytophtora_data = Phytophtora.objects.create(**validated_data)
            for i in data_data:
                Data.objects.create(phytophtora_data=phytophtora_data, **i)
                  
                data_state = validated_data.pop('state')
                phytophtora_state = Phytophtora.objects.create(**validated_data)
                for i in data_state:
                    State.objects.create(phytophtora_state=phytophtora_state, **i)
                      
            return phytophtora_data, phytophtora_state
               
