#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 16:43:21 2024

@author: nicole
"""

from rest_framework import serializers
from elateridi.models import Elateridi, Data, State #, LANGUAGE_CHOICES, STYLE_CHOICES 

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class DataListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = ['LotId', 'year','doy','mean_soil_temperature', 'max_soil_temperature','rain','installation']
        
        
class ElateridiListSerializer(serializers.ModelSerializer):
    
       data=DataListSerializer(many=True)
       state=StateSerializer(required=False)
       class Meta:
           model = Elateridi
          # fields = ['id','data','state']
           fields = '__all__'
           #depth=2 #https://testdriven.io/blog/drf-serializers/

       def create(self, validated_data): #questa serve per i nested dictionaries (https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers)
            data_data = validated_data.pop('data')
            elateridi_data = Elateridi.objects.create(**validated_data)
            for i in data_data:
                Data.objects.create(elateridi_data=elateridi_data, **i)
                  
                data_state = validated_data.pop('state')
                elateridi_state = Elateridi.objects.create(**validated_data)
                for i in data_state:
                    State.objects.create(elateridi_state=elateridi_state, **i)
                      
            return elateridi_data, elateridi_state
               
